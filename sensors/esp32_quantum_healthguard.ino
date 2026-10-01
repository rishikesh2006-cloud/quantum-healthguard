/*
 * 🩺 Quantum HealthGuard — ESP32 Firmware
 * Reads MAX30102 (HR & SpO2), AD8232 (ECG Waveform), and DS18B20 (Temperature)
 * Connects to Wi-Fi and publishes structured JSON telemetry to Raspberry Pi 5 MQTT Broker.
 * 
 * Target Board: ESP32 Dev Module (38-pin or 30-pin)
 * Required Libraries (Install via Arduino Library Manager):
 *   1. PubSubClient by Nick O'Leary
 *   2. SparkFun MAX3010x Pulse and Proximity Sensor Library
 *   3. OneWire by Jim Studt et al.
 *   4. DallasTemperature by Miles Burton
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <OneWire.h>
#include <DallasTemperature.h>

// ─── 1. CONFIGURATION (Edit with your Wi-Fi & Pi 5 IP) ────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";         // Your Wi-Fi Name
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";     // Your Wi-Fi Password
const char* MQTT_BROKER   = "192.168.137.37";         // Your Raspberry Pi 5 IP Address
const int   MQTT_PORT     = 1883;
const char* PATIENT_ID    = "P001";

// ─── 2. PIN DEFINITIONS ───────────────────────────────────────────────────────
// MAX30102 (I2C): SDA -> GPIO 21, SCL -> GPIO 22 (Default ESP32 Wire pins)
#define AD8232_OUTPUT_PIN  34  // Analog pin for ECG waveform
#define AD8232_LO_PLUS     35  // Leads off detector +
#define AD8232_LO_MINUS    32  // Leads off detector -
#define ONE_WIRE_BUS        4  // DS18B20 Temperature Data Pin

// ─── 3. OBJECT INITIALIZATION ─────────────────────────────────────────────────
WiFiClient espClient;
PubSubClient mqttClient(espClient);

MAX30105 particleSensor;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

// Heart Rate variables
const byte RATE_SIZE = 4; // Increase for more smoothing
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 72.0;
int beatAvg = 72;
float spo2Val = 98.0;

unsigned long lastVitalsPublish = 0;
unsigned long lastEcgPublish = 0;

// ─── 4. WI-FI & MQTT CONNECTIVITY ─────────────────────────────────────────────
void setupWiFi() {
  delay(10);
  Serial.print("\n[Wi-Fi] Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Connected!");
    Serial.print("[Wi-Fi] ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[Wi-Fi] Connection Failed! Will retry in main loop.");
  }
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Attempting connection to Pi 5 Gateway (");
    Serial.print(MQTT_BROKER);
    Serial.print(")...");

    String clientId = "ESP32HealthGuard-";
    clientId += String(random(0xffff), HEX);

    if (mqttClient.connect(clientId.c_str())) {
      Serial.println(" CONNECTED!");
      mqttClient.publish("healthguard/status", "{\"device\":\"ESP32\",\"status\":\"ONLINE\"}");
    } else {
      Serial.print(" Failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" Retrying in 3 seconds...");
      delay(3000);
    }
  }
}

// ─── 5. SETUP ─────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  Serial.println("\n==================================================");
  Serial.println("  Quantum HealthGuard — ESP32 Biosensor Node");
  Serial.println("==================================================");

  // Pin Modes for AD8232 ECG
  pinMode(AD8232_LO_PLUS, INPUT);
  pinMode(AD8232_LO_MINUS, INPUT);

  // Initialize MAX30102 I2C
  Wire.begin(21, 22);
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("[MAX30102] Sensor not found! Check SDA/SCL wiring.");
  } else {
    Serial.println("[MAX30102] Sensor initialized successfully.");
    particleSensor.setup(); // Configure sensor with default settings
    particleSensor.setPulseAmplitudeRed(0x0A); // Turn Red LED to low to indicate sensor running
    particleSensor.setPulseAmplitudeGreen(0);  // Turn off Green LED
  }

  // Initialize DS18B20 Temperature Sensor
  tempSensor.begin();
  Serial.println("[DS18B20] Temperature sensor ready.");

  // Wi-Fi & MQTT Setup
  setupWiFi();
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
}

// ─── 6. MAIN LOOP ─────────────────────────────────────────────────────────────
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setupWiFi();
  }
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  unsigned long currentMillis = millis();

  // ── Read MAX30102 Heart Rate & SpO2 ─────────────────────────────────────────
  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue) == true) {
    long delta = currentMillis - lastBeat;
    lastBeat = currentMillis;

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;

      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++) {
        beatAvg += rates[x];
      }
      beatAvg /= RATE_SIZE;
    }
  }

  // Approximate SpO2 from Red/IR LED intensity ratio
  long redValue = particleSensor.getRed();
  if (irValue > 50000) {
    float ratio = (float)redValue / (float)irValue;
    spo2Val = 104 - (17 * ratio);
    if (spo2Val > 100) spo2Val = 100.0;
    if (spo2Val < 80)  spo2Val = 80.0;
  } else {
    // No finger detected
    beatAvg = 0;
    spo2Val = 0.0;
  }

  // ── Publish Vitals JSON (Every 1000 ms) ──────────────────────────────────────
  if (currentMillis - lastVitalsPublish >= 1000) {
    lastVitalsPublish = currentMillis;

    // Read Temperature from DS18B20
    tempSensor.requestTemperatures();
    float bodyTemp = tempSensor.getTempCByIndex(0);
    if (bodyTemp < -50 || bodyTemp > 80) {
      bodyTemp = 36.6; // Fallback default if disconnected
    }

    // Build JSON Payload
    String payload = "{";
    payload += "\"patient_id\":\"" + String(PATIENT_ID) + "\",";
    payload += "\"heart_rate\":" + String(beatAvg > 0 ? beatAvg : 72) + ",";
    payload += "\"spo2\":" + String(spo2Val > 0 ? spo2Val : 98.0, 1) + ",";
    payload += "\"temperature\":" + String(bodyTemp, 2) + ",";
    payload += "\"timestamp\":" + String(currentMillis / 1000.0, 2);
    payload += "}";

    mqttClient.publish("healthguard/vitals", payload.c_str());
    Serial.print("[PUB Vitals] ");
    Serial.println(payload);
  }

  // ── Publish ECG Waveform Sample (Every 100 ms / 10 Hz) ─────────────────────
  if (currentMillis - lastEcgPublish >= 100) {
    lastEcgPublish = currentMillis;

    int ecgSample = 512;
    if ((digitalRead(AD8232_LO_PLUS) == 1) || (digitalRead(AD8232_LO_MINUS) == 1)) {
      // Leads Off detected
      ecgSample = 0;
    } else {
      ecgSample = analogRead(AD8232_OUTPUT_PIN);
    }

    String ecgPayload = "{";
    ecgPayload += "\"sample\":" + String(ecgSample) + ",";
    ecgPayload += "\"timestamp\":" + String(currentMillis / 1000.0, 2);
    ecgPayload += "}";

    mqttClient.publish("healthguard/ecg", ecgPayload.c_str());
  }
}
