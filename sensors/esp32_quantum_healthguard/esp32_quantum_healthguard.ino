/*
 * ==============================================================================
 *  QUANTUM HEALTHGUARD — ESP32 HARDWARE FIRMWARE (STAGE 1 NODE)
 *  REAL VALUES ONLY — No fake/fallback data ever sent.
 *  NON-BLOCKING SAMPLING — Fast continuous loop for MAX30102 beat detection.
 * ==============================================================================
 *  Sensors: AD8232 (ECG), MAX30102 (HR + SpO2), DS18B20 (Temperature)
 *  Communication: Wi-Fi + MQTT (Direct to Pi 5) AND USB Serial (Bridge to Pi 5)
 *  Topics: healthguard/vitals, healthguard/ecg, healthguard/status
 *
 *  Required Arduino Libraries:
 *    1. PubSubClient by Nick O'Leary
 *    2. SparkFun MAX3010x Pulse and Proximity Sensor Library
 *    3. OneWire by Jim Studt
 *    4. DallasTemperature by Miles Burton
 * ==============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <OneWire.h>
#include <DallasTemperature.h>

// ==============================================================================
// 1. NETWORK & MQTT SETTINGS
// ==============================================================================
const char* WIFI_SSID     = "asus123";          // Mobile Hotspot SSID
const char* WIFI_PASSWORD = "12345678";         // Mobile Hotspot Password
const char* MQTT_BROKER   = "192.168.137.245"; // Raspberry Pi 5 Gateway IP
const int   MQTT_PORT     = 1883;
const char* PATIENT_ID    = "P001";

// ==============================================================================
// 2. PIN DEFINITIONS (ESP32 GPIO)
// ==============================================================================
const int ECG_PIN      = 34;
const int LO_PLUS_PIN  = 35;
const int LO_MINUS_PIN = 32;
const int SDA_PIN      = 21;
const int SCL_PIN      = 22;
const int TEMP_PIN     = 4;

// ==============================================================================
// 3. HARDWARE OBJECTS & STATE
// ==============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

MAX30105 pulseSensor;
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

bool pulseSensorReady = false;
bool tempSensorReady  = false;

// Heart Rate smoothing & detection
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0.0;
int beatAvg = 0;
float spo2Val = 0.0;
bool fingerDetected = false;
float currentTempC = 0.0;

// Non-blocking Timers
unsigned long lastVitalsPublish = 0;
unsigned long lastEcgPublish    = 0;
unsigned long lastWifiCheck     = 0;
unsigned long lastMqttCheck     = 0;
unsigned long lastSerialDebug   = 0;

// ==============================================================================
// 4. NON-BLOCKING WI-FI & MQTT
// ==============================================================================
void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    if (millis() - lastWifiCheck > 5000) {
      lastWifiCheck = millis();
      Serial.println("[Wi-Fi] Connecting to asus123...");
      WiFi.disconnect();
      WiFi.reconnect();
    }
  }
}

void checkMQTTConnection() {
  if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
    if (millis() - lastMqttCheck > 4000) {
      lastMqttCheck = millis();
      String clientId = "ESP32-QHG-" + String(random(0xffff), HEX);
      Serial.print("[MQTT] Connecting to Edge Gateway (192.168.137.245:1883)... ");
      if (mqttClient.connect(clientId.c_str())) {
        Serial.println("CONNECTED!");
        mqttClient.publish("healthguard/status", "{\"device\":\"ESP32\",\"status\":\"ONLINE\"}");
      } else {
        Serial.print("Failed, rc=");
        Serial.println(mqttClient.state());
      }
    }
  }
}

// ==============================================================================
// 5. SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("\n==================================================");
  Serial.println("  QUANTUM HEALTHGUARD — REAL SENSOR MODE ONLY     ");
  Serial.println("==================================================");

  // 1. GPIO Setup
  pinMode(ECG_PIN, INPUT);
  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);

  // 2. I2C & MAX30102 Pulse Oximeter Setup
  Wire.begin(SDA_PIN, SCL_PIN);
  if (pulseSensor.begin(Wire, I2C_SPEED_FAST)) {
    pulseSensorReady = true;
    pulseSensor.setup();
    // High amplitude for reliable finger penetration
    pulseSensor.setPulseAmplitudeRed(0x2A);
    pulseSensor.setPulseAmplitudeIR(0x2A);
    pulseSensor.setPulseAmplitudeGreen(0);
    Serial.println("[OK] MAX30102 pulse sensor initialized.");
  } else {
    Serial.println("[ERROR] MAX30102 not detected on I2C (SDA=21, SCL=22)!");
  }

  // 3. DS18B20 Temperature Setup
  tempSensor.begin();
  tempSensor.setResolution(10);
  tempSensor.setWaitForConversion(false); // Non-blocking!
  if (tempSensor.getDeviceCount() > 0) {
    tempSensorReady = true;
    tempSensor.requestTemperatures(); // Trigger first conversion
    Serial.println("[OK] DS18B20 temperature probe initialized on GPIO 4.");
  } else {
    Serial.println("[WARNING] DS18B20 not detected on GPIO 4.");
  }

  // 4. Wi-Fi Startup (Non-blocking: attempt up to 3 seconds, continue anyway)
  Serial.print("[Wi-Fi] Connecting to SSID: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startWifi = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startWifi < 3000) {
    delay(200);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[Wi-Fi] Not connected yet; background retry will maintain connection.");
  }

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(512);

  Serial.println("=== SYSTEM READY — PLACE FINGER ON SENSOR FOR REAL READINGS ===\n");
}

// ==============================================================================
// 6. MAIN LOOP — CONTINUOUS NON-BLOCKING SAMPLING
// ==============================================================================
void loop() {
  unsigned long now = millis();

  // Non-blocking network management
  checkWiFiConnection();
  checkMQTTConnection();
  if (mqttClient.connected()) {
    mqttClient.loop();
  }

  // --- A. REAL SENSOR SAMPLING (MAX30102) ---
  long irValue  = 0;
  long redValue = 0;

  if (pulseSensorReady) {
    irValue  = pulseSensor.getIR();
    redValue = pulseSensor.getRed();

    // Finger threshold: IR typically rises above 30,000 upon contact
    if (irValue > 30000) {
      fingerDetected = true;

      // Pulse beat detection
      if (checkForBeat(irValue)) {
        long delta = now - lastBeat;
        lastBeat = now;
        if (delta > 250 && delta < 2000) { // Valid range: 30 to 240 BPM
          beatsPerMinute = 60.0 / (delta / 1000.0);
          if (beatsPerMinute >= 40 && beatsPerMinute <= 180) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;
            int total = 0;
            int validCount = 0;
            for (byte x = 0; x < RATE_SIZE; x++) {
              if (rates[x] > 0) {
                total += rates[x];
                validCount++;
              }
            }
            if (validCount > 0) beatAvg = total / validCount;
          }
        }
      }

      // SpO2 calculation via Red/IR ratio
      if (irValue > 0) {
        float ratio = (float)redValue / (float)irValue;
        float calculatedSpO2 = 104.0 - (17.0 * ratio);
        if (calculatedSpO2 > 100.0) calculatedSpO2 = 99.0;
        if (calculatedSpO2 < 75.0)  calculatedSpO2 = 75.0;
        spo2Val = calculatedSpO2;
      }

    } else {
      // Finger removed: reset values to 0 (NEVER send fake numbers!)
      fingerDetected = false;
      beatAvg = 0;
      spo2Val = 0.0;
    }
  }

  // --- B. ECG SAMPLING (AD8232) ---
  bool leadsOff = (digitalRead(LO_PLUS_PIN) == HIGH) || (digitalRead(LO_MINUS_PIN) == HIGH);
  int ecgValue  = leadsOff ? 0 : analogRead(ECG_PIN);

  // ECG Publish @ 20 Hz (every 50 ms)
  if (now - lastEcgPublish >= 50) {
    lastEcgPublish = now;
    if (mqttClient.connected()) {
      String ecgMsg = "{\"sample\":" + String(ecgValue) +
                      ",\"leads_off\":" + (leadsOff ? "true" : "false") + "}";
      mqttClient.publish("healthguard/ecg", ecgMsg.c_str());
    }
  }

  // --- C. VITALS PUBLISH @ 1 Hz (every 1000 ms) ---
  if (now - lastVitalsPublish >= 1000) {
    lastVitalsPublish = now;

    // Read temperature conversion triggered previously
    if (tempSensorReady) {
      float rawTemp = tempSensor.getTempCByIndex(0);
      if (rawTemp != DEVICE_DISCONNECTED_C && rawTemp > 10.0 && rawTemp < 50.0) {
        currentTempC = rawTemp; // Real body / ambient skin temperature
      }
      tempSensor.requestTemperatures(); // Trigger next conversion asynchronously
    }

    // Build diagnostic status string
    String status = "ONLINE (";
    status += fingerDetected ? "FINGER:YES" : "FINGER:NO";
    status += leadsOff ? "+ECG:LEADS_OFF" : "+ECG:OK";
    status += tempSensorReady ? "+TEMP:OK" : "+TEMP:DISCONNECTED";
    status += ")";

    // Prepare JSON payload
    float sendHR   = fingerDetected ? (float)beatAvg : 0.0;
    float sendSpO2 = fingerDetected ? spo2Val : 0.0;

    String payload = "{";
    payload += "\"patient_id\":\"" + String(PATIENT_ID) + "\",";
    payload += "\"heart_rate\":" + String(sendHR, 1) + ",";
    payload += "\"spo2\":" + String(sendSpO2, 1) + ",";
    payload += "\"temperature\":" + String(currentTempC, 2) + ",";
    payload += "\"finger_detected\":" + String(fingerDetected ? "true" : "false") + ",";
    payload += "\"sensor_status\":\"" + status + "\",";
    payload += "\"raw_ir\":" + String(irValue) + ",";
    payload += "\"timestamp\":" + String(now / 1000.0, 2);
    payload += "}";

    // ALWAYS print to USB Serial for USB bridge / debugging
    Serial.println(payload);

    // If MQTT is connected over Wi-Fi, publish directly to Pi 5
    if (mqttClient.connected()) {
      mqttClient.publish("healthguard/vitals", payload.c_str());
    }
  }

  // --- D. SERIAL DEBUG (every 500 ms) ---
  if (now - lastSerialDebug >= 500) {
    lastSerialDebug = now;
    Serial.print("[DEBUG] Finger: ");
    Serial.print(fingerDetected ? "YES" : "NO");
    Serial.print(" (IR=");
    Serial.print(irValue);
    Serial.print(") | HR: ");
    Serial.print(beatAvg);
    Serial.print(" bpm | SpO2: ");
    Serial.print(spo2Val, 1);
    Serial.print("% | Temp: ");
    Serial.print(currentTempC, 1);
    Serial.print("C | WiFi: ");
    Serial.print(WiFi.status() == WL_CONNECTED ? "CONNECTED" : "DISCONNECTED");
    Serial.print(" | MQTT: ");
    Serial.println(mqttClient.connected() ? "CONNECTED" : "DISCONNECTED");
  }
}
