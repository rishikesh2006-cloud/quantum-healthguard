/*
 * ==============================================================================
 *  QUANTUM HEALTHGUARD — ESP32 HARDWARE FIRMWARE (STAGE 1 NODE)
 *  REAL VALUES ONLY — No fake/fallback data ever sent.
 * ==============================================================================
 *  Sensors: AD8232 (ECG), MAX30102 (HR + SpO2), DS18B20 (Temperature)
 *  Communication: Wi-Fi + MQTT to Raspberry Pi 5 / Laptop
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
// 1. NETWORK & MQTT SETTINGS — CHANGE THESE 3 LINES BEFORE UPLOADING
// ==============================================================================
const char* WIFI_SSID     = "YOUR_WIFI_SSID";      // <-- Your Wi-Fi Name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // <-- Your Wi-Fi Password
const char* MQTT_BROKER   = "192.168.137.1";       // <-- IP of Raspberry Pi 5 or Laptop
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
// 3. HARDWARE OBJECTS
// ==============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

MAX30105 pulseSensor;
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

bool pulseSensorReady = false;
bool tempSensorReady  = false;

// Heart Rate smoothing
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0.0;
int beatAvg = 0;
float spo2Val = 0.0;
bool fingerDetected = false;

// Timers
unsigned long lastVitalsPublish = 0;
unsigned long lastEcgPublish    = 0;
unsigned long lastSerialDebug   = 0;

// ==============================================================================
// 4. WI-FI & MQTT
// ==============================================================================
void setupWiFi() {
  Serial.print("\n[Wi-Fi] Connecting to: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Connected!");
    Serial.print("[Wi-Fi] ESP32 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[Wi-Fi] Failed. Will retry.");
  }
}

void reconnectMQTT() {
  if (WiFi.status() != WL_CONNECTED) return;
  if (!mqttClient.connected()) {
    String clientId = "ESP32-QHG-" + String(random(0xffff), HEX);
    if (mqttClient.connect(clientId.c_str())) {
      Serial.println("[MQTT] Connected to Gateway!");
      mqttClient.publish("healthguard/status", "{\"device\":\"ESP32\",\"status\":\"ONLINE\"}");
    }
  }
}

// ==============================================================================
// 5. SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== QUANTUM HEALTHGUARD — REAL SENSOR MODE ===");

  pinMode(ECG_PIN, INPUT);
  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);

  Wire.begin(SDA_PIN, SCL_PIN);
  if (pulseSensor.begin(Wire, I2C_SPEED_FAST)) {
    pulseSensorReady = true;
    pulseSensor.setup();
    pulseSensor.setPulseAmplitudeRed(0x1F);
    pulseSensor.setPulseAmplitudeIR(0x1F);
    pulseSensor.setPulseAmplitudeGreen(0);
    Serial.println("[OK] MAX30102 detected.");
  } else {
    Serial.println("[ERROR] MAX30102 not found!");
  }

  tempSensor.begin();
  tempSensor.setResolution(10);
  tempSensor.setWaitForConversion(false);
  if (tempSensor.getDeviceCount() > 0) {
    tempSensorReady = true;
    Serial.println("[OK] DS18B20 detected.");
  } else {
    Serial.println("[WARNING] DS18B20 not found.");
  }

  setupWiFi();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(512);

  Serial.println("=== SENDING REAL VALUES ONLY — NO FAKE DATA ===\n");
}

// ==============================================================================
// 6. MAIN LOOP — REAL VALUES ONLY
// ==============================================================================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  } else if (!mqttClient.connected()) {
    static unsigned long lastRetry = 0;
    if (millis() - lastRetry > 3000) {
      lastRetry = millis();
      reconnectMQTT();
    }
  }
  mqttClient.loop();

  unsigned long now = millis();

  // --- A. READ SENSORS (REAL VALUES) ---
  long irValue  = 0;
  long redValue = 0;

  if (pulseSensorReady) {
    irValue  = pulseSensor.getIR();
    redValue = pulseSensor.getRed();

    // Only calculate HR/SpO2 when finger is actually on the sensor
    if (irValue > 50000) {
      fingerDetected = true;

      if (checkForBeat(irValue)) {
        long delta = now - lastBeat;
        lastBeat = now;
        if (delta > 0) {
          beatsPerMinute = 60.0 / (delta / 1000.0);
          if (beatsPerMinute >= 30 && beatsPerMinute <= 220) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;
            beatAvg = 0;
            for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
            beatAvg /= RATE_SIZE;
          }
        }
      }

      float ratio = (float)redValue / (float)irValue;
      spo2Val = 104.0 - (17.0 * ratio);
      if (spo2Val > 100.0) spo2Val = 100.0;
      if (spo2Val < 70.0)  spo2Val = 70.0;

    } else {
      // NO FINGER on sensor — send ZERO (not fake values)
      fingerDetected = false;
      beatAvg = 0;
      spo2Val = 0.0;
    }
  }

  bool leadsOff = (digitalRead(LO_PLUS_PIN) == HIGH) || (digitalRead(LO_MINUS_PIN) == HIGH);
  int ecgValue  = leadsOff ? 0 : analogRead(ECG_PIN);

  // --- B. PUBLISH ECG (20 Hz) ---
  if (now - lastEcgPublish >= 50) {
    lastEcgPublish = now;
    if (mqttClient.connected()) {
      String ecg = "{\"sample\":" + String(ecgValue) +
                   ",\"leads_off\":" + String(leadsOff ? "true" : "false") + "}";
      mqttClient.publish("healthguard/ecg", ecg.c_str());
    }
  }

  // --- C. PUBLISH VITALS (1 Hz) — REAL VALUES ONLY ---
  if (now - lastVitalsPublish >= 1000) {
    lastVitalsPublish = now;

    // Temperature: Send REAL reading only (0.0 if sensor not connected)
    float tempC = 0.0;
    if (tempSensorReady) {
      tempSensor.requestTemperatures();
      float raw = tempSensor.getTempCByIndex(0);
      if (raw != DEVICE_DISCONNECTED_C && raw > 10.0 && raw < 50.0) {
        tempC = raw;  // REAL body temperature
      }
    }

    // Sensor status string
    String status = "ONLINE (";
    status += fingerDetected ? "FINGER:YES" : "FINGER:NO";
    status += leadsOff ? "+ECG:LEADS_OFF" : "+ECG:OK";
    status += tempSensorReady ? "+TEMP:OK" : "+TEMP:DISCONNECTED";
    status += ")";

    // Heart Rate & SpO2: Send REAL values (0 if no finger)
    // NO FAKE FALLBACK VALUES — dashboard will show "Waiting for sensor"
    float sendHR   = (float)beatAvg;    // 0 when no finger
    float sendSpO2 = spo2Val;           // 0.0 when no finger

    String payload = "{";
    payload += "\"patient_id\":\"" + String(PATIENT_ID) + "\",";
    payload += "\"heart_rate\":" + String(sendHR, 1) + ",";
    payload += "\"spo2\":" + String(sendSpO2, 1) + ",";
    payload += "\"temperature\":" + String(tempC, 2) + ",";
    payload += "\"finger_detected\":" + String(fingerDetected ? "true" : "false") + ",";
    payload += "\"sensor_status\":\"" + status + "\",";
    payload += "\"timestamp\":" + String(now / 1000.0, 2);
    payload += "}";

    if (mqttClient.connected()) {
      mqttClient.publish("healthguard/vitals", payload.c_str());
      Serial.print("[REAL DATA] ");
      Serial.println(payload);
    }
  }

  // --- D. SERIAL DEBUG (5 Hz) ---
  if (now - lastSerialDebug >= 200) {
    lastSerialDebug = now;
    Serial.print("Finger:");
    Serial.print(fingerDetected ? "YES" : "NO");
    Serial.print(" | HR:");
    Serial.print(beatAvg);
    Serial.print(" | SpO2:");
    Serial.print(spo2Val, 1);
    Serial.print(" | Temp:");
    if (tempSensorReady) {
      float t = tempSensor.getTempCByIndex(0);
      if (t != DEVICE_DISCONNECTED_C && t > 10.0) Serial.print(t, 1);
      else Serial.print("--");
    } else {
      Serial.print("NC");
    }
    Serial.print(" | ECG:");
    Serial.println(ecgValue);
  }
}
