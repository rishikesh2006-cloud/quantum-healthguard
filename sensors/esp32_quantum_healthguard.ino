/*
 * ==============================================================================
 *  QUANTUM HEALTHGUARD — ESP32 HARDWARE FIRMWARE (STAGE 1 NODE)
 * ==============================================================================
 *  Compatible with: AD8232 (ECG), MAX30102 (HR + SpO2), DS18B20 (Temperature)
 *  Integrates directly with:
 *    - Stage 2: Raspberry Pi 5 / Laptop MQTT Broker (1883)
 *    - Topics: healthguard/vitals, healthguard/ecg, healthguard/status
 *    - Live Dashboard & Dual QSVC/Random Forest ML Classifier
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
// 1. NETWORK & MQTT SETTINGS (Configure for your Local Wi-Fi & Gateway)
// ==============================================================================
const char* WIFI_SSID     = "YOUR_WIFI_SSID";      // <-- Enter your Wi-Fi Name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";  // <-- Enter your Wi-Fi Password
const char* MQTT_BROKER   = "192.168.1.100";       // <-- IP of Raspberry Pi 5 or Laptop running main.py
const int   MQTT_PORT     = 1883;
const char* PATIENT_ID    = "P001";

// ==============================================================================
// 2. PIN DEFINITIONS (ESP32 GPIO)
// ==============================================================================
// ECG Sensor (AD8232)
const int ECG_PIN      = 34; // Analog ECG output
const int LO_PLUS_PIN  = 35; // Leads-off detector +
const int LO_MINUS_PIN = 32; // Leads-off detector -

// MAX30102 I2C Pins
const int SDA_PIN      = 21; // ESP32 Default SDA
const int SCL_PIN      = 22; // ESP32 Default SCL

// DS18B20 Temperature Sensor (Requires 4.7k pull-up resistor to 3.3V)
const int TEMP_PIN     = 4;

// ==============================================================================
// 3. HARDWARE & CLIENT OBJECTS
// ==============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

MAX30105 pulseSensor;
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

// Sensor state flags
bool pulseSensorReady = false;
bool tempSensorReady  = false;

// Heart Rate calculation smoothing
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 72.0;
int beatAvg = 72;
float spo2Val = 98.0;

// Non-blocking timers
unsigned long lastVitalsPublish = 0;
unsigned long lastEcgPublish    = 0;
unsigned long lastSerialDebug   = 0;

// ==============================================================================
// 4. WI-FI & MQTT MANAGEMENT
// ==============================================================================
void setupWiFi() {
  delay(10);
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
    Serial.println("\n[Wi-Fi] Connected Successfully!");
    Serial.print("[Wi-Fi] ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[Wi-Fi] Connection Failed (Will retry in loop)");
  }
}

void reconnectMQTT() {
  if (WiFi.status() != WL_CONNECTED) return;

  if (!mqttClient.connected()) {
    Serial.print("[MQTT] Connecting to Gateway (");
    Serial.print(MQTT_BROKER);
    Serial.print(")...");

    String clientId = "ESP32-QuantumHealthGuard-";
    clientId += String(random(0xffff), HEX);

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println(" CONNECTED!");
      mqttClient.publish("healthguard/status", "{\"device\":\"ESP32\",\"status\":\"ONLINE\"}");
    } else {
      Serial.print(" Failed (rc=");
      Serial.print(mqttClient.state());
      Serial.println("). Retrying shortly...");
    }
  }
}

// ==============================================================================
// 5. SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=======================================================");
  Serial.println("  QUANTUM HEALTHGUARD — ESP32 MULTI-SENSOR NODE");
  Serial.println("=======================================================");

  // 1. Configure ECG pins (AD8232)
  pinMode(ECG_PIN, INPUT);
  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);

  // 2. Initialize I2C for MAX30102
  Wire.begin(SDA_PIN, SCL_PIN);
  if (pulseSensor.begin(Wire, I2C_SPEED_FAST)) {
    pulseSensorReady = true;
    pulseSensor.setup();
    pulseSensor.setPulseAmplitudeRed(0x1F);
    pulseSensor.setPulseAmplitudeIR(0x1F);
    pulseSensor.setPulseAmplitudeGreen(0);
    Serial.println("[OK] MAX30102 Pulse Oximeter initialized.");
  } else {
    Serial.println("[ERROR] MAX30102 not detected! Check SDA(21), SCL(22), 3.3V, GND.");
  }

  // 3. Initialize DS18B20 Temperature Sensor
  tempSensor.begin();
  tempSensor.setResolution(10);
  tempSensor.setWaitForConversion(false); // Non-blocking reads
  if (tempSensor.getDeviceCount() > 0) {
    tempSensorReady = true;
    Serial.println("[OK] DS18B20 Temperature Sensor detected.");
  } else {
    Serial.println("[WARNING] DS18B20 not detected. Verify 4.7k pull-up on GPIO 4.");
  }

  // 4. Setup Wi-Fi & MQTT Client
  setupWiFi();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(512);

  Serial.println("-------------------------------------------------------");
  Serial.println("Telemetry ready: Publishing to Quantum HealthGuard pipeline.");
  Serial.println("-------------------------------------------------------\n");
}

// ==============================================================================
// 6. MAIN LOOP
// ==============================================================================
void loop() {
  // Maintain connectivity
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  } else if (!mqttClient.connected()) {
    static unsigned long lastMqttRetry = 0;
    if (millis() - lastMqttRetry > 3000) {
      lastMqttRetry = millis();
      reconnectMQTT();
    }
  }
  mqttClient.loop();

  unsigned long currentMillis = millis();

  // ----------------------------------------------------------------------------
  // A. SENSOR DATA ACQUISITION & CONTINUOUS BEAT DETECTION
  // ----------------------------------------------------------------------------
  long irValue  = 0;
  long redValue = 0;

  if (pulseSensorReady) {
    irValue  = pulseSensor.getIR();
    redValue = pulseSensor.getRed();

    // Check for heart beat if finger is present (IR > 50,000)
    if (irValue > 50000) {
      if (checkForBeat(irValue)) {
        long delta = currentMillis - lastBeat;
        lastBeat = currentMillis;

        if (delta > 0) {
          beatsPerMinute = 60.0 / (delta / 1000.0);

          if (beatsPerMinute >= 30 && beatsPerMinute <= 220) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;

            beatAvg = 0;
            for (byte x = 0; x < RATE_SIZE; x++) {
              beatAvg += rates[x];
            }
            beatAvg /= RATE_SIZE;
          }
        }
      }

      // SpO2 estimation using Red/IR ratio
      float ratio = (float)redValue / (float)irValue;
      spo2Val = 104.0 - (17.0 * ratio);
      if (spo2Val > 100.0) spo2Val = 100.0;
      if (spo2Val < 70.0)  spo2Val = 70.0;

    } else {
      // Finger not detected on sensor
      beatAvg = 0;
      spo2Val = 0.0;
    }
  }

  // Read ECG signal and leads-off status
  bool leadsOff = (digitalRead(LO_PLUS_PIN) == HIGH) || (digitalRead(LO_MINUS_PIN) == HIGH);
  int ecgValue  = leadsOff ? 0 : analogRead(ECG_PIN);

  // ----------------------------------------------------------------------------
  // B. PUBLISH ECG WAVEFORM (Every 50 ms / 20 Hz for Live Oscilloscope)
  // ----------------------------------------------------------------------------
  if (currentMillis - lastEcgPublish >= 50) {
    lastEcgPublish = currentMillis;

    if (mqttClient.connected()) {
      String ecgPayload = "{";
      ecgPayload += "\"sample\":" + String(ecgValue) + ",";
      ecgPayload += "\"leads_off\":" + String(leadsOff ? "true" : "false") + ",";
      ecgPayload += "\"timestamp\":" + String(currentMillis / 1000.0, 2);
      ecgPayload += "}";

      mqttClient.publish("healthguard/ecg", ecgPayload.c_str());
    }
  }

  // ----------------------------------------------------------------------------
  // C. PUBLISH VITAL SIGNS TELEMETRY TO STAGE 2 EDGE (Every 1000 ms / 1 Hz)
  // ----------------------------------------------------------------------------
  if (currentMillis - lastVitalsPublish >= 1000) {
    lastVitalsPublish = currentMillis;

    // Fetch DS18B20 Temperature
    float tempC = 36.6; // Nominal default fallback
    if (tempSensorReady) {
      tempSensor.requestTemperatures();
      float readTemp = tempSensor.getTempCByIndex(0);
      if (readTemp != DEVICE_DISCONNECTED_C && readTemp > 0.0 && readTemp < 60.0) {
        tempC = readTemp;
      }
    }

    // Determine sensor health status
    String statusStr = "ONLINE (";
    statusStr += (leadsOff ? "ECG:LEADS_OFF" : "ECG:OK");
    statusStr += (pulseSensorReady && irValue > 50000 ? "+MAX30102:OK" : "+MAX30102:NO_FINGER");
    statusStr += (tempSensorReady ? "+DS18B20:OK" : "+DS18B20:FAIL");
    statusStr += ")";

    // Prepare values for Stage 2 Edge & Stage 3 AI Predictor
    float pubHR   = (beatAvg > 0) ? (float)beatAvg : 72.0;
    float pubSpO2 = (spo2Val > 0.0) ? spo2Val : 98.0;

    // Build compatible JSON payload for Stage 2 Edge Processor
    String vitalsPayload = "{";
    vitalsPayload += "\"patient_id\":\"" + String(PATIENT_ID) + "\",";
    vitalsPayload += "\"heart_rate\":" + String(pubHR, 1) + ",";
    vitalsPayload += "\"spo2\":" + String(pubSpO2, 1) + ",";
    vitalsPayload += "\"temperature\":" + String(tempC, 2) + ",";
    vitalsPayload += "\"sensor_status\":\"" + statusStr + "\",";
    vitalsPayload += "\"timestamp\":" + String(currentMillis / 1000.0, 2);
    vitalsPayload += "}";

    if (mqttClient.connected()) {
      mqttClient.publish("healthguard/vitals", vitalsPayload.c_str());
      Serial.print("[PUB Vitals] ");
      Serial.println(vitalsPayload);
    } else {
      Serial.print("[LOCAL Vitals] (MQTT Disconnected): ");
      Serial.println(vitalsPayload);
    }
  }

  // ----------------------------------------------------------------------------
  // D. SERIAL MONITOR DEBUG OUTPUT (Compatible with your test output)
  // ----------------------------------------------------------------------------
  if (currentMillis - lastSerialDebug >= 200) {
    lastSerialDebug = currentMillis;

    Serial.print("ECG=");
    Serial.print(ecgValue);
    Serial.print(", LeadsOff=");
    Serial.print(leadsOff ? "YES" : "NO");
    Serial.print(", IR=");
    Serial.print(irValue);
    Serial.print(", RED=");
    Serial.print(redValue);
    Serial.print(", HR_BPM=");
    Serial.print(beatAvg);
    Serial.print(", SpO2=");
    Serial.print(spo2Val, 1);
    Serial.print(", Temp_C=");
    Serial.println(tempSensorReady ? String(tempSensor.getTempCByIndex(0), 1) : "Error");
  }
}
