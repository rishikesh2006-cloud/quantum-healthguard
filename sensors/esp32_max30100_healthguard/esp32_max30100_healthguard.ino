/*
 * ==============================================================================
 *  QUANTUM HEALTHGUARD — ESP32 FIRMWARE (MAX30100 VERSION)
 *  Compatible with MAX30100 Pulse Oximeter, DS18B20 Temp, and AD8232 ECG
 *  Transmits to Stage 2 Raspberry Pi 5 Gateway & Live Dashboard
 * ==============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include "MAX30100_PulseOximeter.h"
#include <OneWire.h>
#include <DallasTemperature.h>

// ==============================================================================
// 1. NETWORK & GATEWAY CONFIGURATION
// ==============================================================================
const char* WIFI_SSID     = "asus123";          // Mobile Hotspot SSID
const char* WIFI_PASSWORD = "12345678";         // Mobile Hotspot Password
const char* MQTT_BROKER   = "192.168.137.245"; // Raspberry Pi 5 Edge Gateway IP
const int   MQTT_PORT     = 1883;
const char* PATIENT_ID    = "P001";

// ==============================================================================
// 2. PIN DEFINITIONS
// ==============================================================================
const int SDA_PIN      = 21; // MAX30100 I2C SDA
const int SCL_PIN      = 22; // MAX30100 I2C SCL
const int TEMP_PIN     = 4;  // DS18B20 OneWire Data (Requires 4.7k pull-up)
const int ECG_PIN      = 34; // AD8232 Analog Output
const int LO_PLUS_PIN  = 35; // AD8232 Leads-off +
const int LO_MINUS_PIN = 32; // AD8232 Leads-off -

// ==============================================================================
// 3. OBJECTS & STATE
// ==============================================================================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

PulseOximeter pox;
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

bool poxReady       = false;
bool tempSensorReady = false;

float currentHR   = 0.0;
float currentSpO2 = 0.0;
float currentTemp = 0.0;

unsigned long lastReportTime    = 0;
unsigned long lastEcgPublish    = 0;
unsigned long lastWifiCheck     = 0;
unsigned long lastMqttCheck     = 0;

void onBeatDetected() {
  Serial.println("[BEAT] Heart beat detected!");
}

// ==============================================================================
// 4. NON-BLOCKING WI-FI & MQTT
// ==============================================================================
void checkWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    if (millis() - lastWifiCheck > 5000) {
      lastWifiCheck = millis();
      Serial.println("[Wi-Fi] Connecting to asus123...");
      WiFi.disconnect();
      WiFi.reconnect();
    }
  }
}

void checkMQTT() {
  if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
    if (millis() - lastMqttCheck > 4000) {
      lastMqttCheck = millis();
      String clientId = "ESP32-QHG-" + String(random(0xffff), HEX);
      Serial.print("[MQTT] Connecting to Pi 5 Gateway (192.168.137.245)... ");
      if (mqttClient.connect(clientId.c_str())) {
        Serial.println("CONNECTED!");
        mqttClient.publish("healthguard/status", "{\"device\":\"ESP32\",\"status\":\"ONLINE\"}");
      } else {
        Serial.print("Failed (rc=");
        Serial.print(mqttClient.state());
        Serial.println(")");
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

  Serial.println("\n=======================================================");
  Serial.println("  QUANTUM HEALTHGUARD — MAX30100 MULTI-SENSOR NODE");
  Serial.println("=======================================================");

  // 1. ECG Pins
  pinMode(ECG_PIN, INPUT);
  pinMode(LO_PLUS_PIN, INPUT);
  pinMode(LO_MINUS_PIN, INPUT);

  // 2. Initialize I2C and MAX30100
  Wire.begin(SDA_PIN, SCL_PIN);
  Serial.println("[INIT] Initializing MAX30100 sensor on I2C (21, 22)...");
  
  if (!pox.begin()) {
    Serial.println("[ERROR] MAX30100 not detected! Check 3.3V, GND, SDA(21), SCL(22).");
  } else {
    poxReady = true;
    pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);
    pox.setOnBeatDetectedCallback(onBeatDetected);
    Serial.println("[OK] MAX30100 connected successfully!");
  }

  // 3. Initialize DS18B20 Temperature
  tempSensor.begin();
  tempSensor.setResolution(10);
  tempSensor.setWaitForConversion(false);
  if (tempSensor.getDeviceCount() > 0) {
    tempSensorReady = true;
    tempSensor.requestTemperatures();
    Serial.println("[OK] DS18B20 temperature probe detected on GPIO 4.");
  } else {
    Serial.println("[WARNING] DS18B20 not found on GPIO 4.");
  }

  // 4. Wi-Fi (Non-blocking attempt up to 3 seconds)
  Serial.print("[Wi-Fi] Connecting to SSID: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  unsigned long startW = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startW < 3000) {
    delay(200);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[Wi-Fi] Connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[Wi-Fi] Background retry will maintain connection.");
  }

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setBufferSize(512);

  Serial.println("=======================================================");
  Serial.println("  SYSTEM READY — PLACE FINGER ON SENSOR FOR REAL DATA");
  Serial.println("=======================================================\n");
}

// ==============================================================================
// 6. MAIN LOOP
// ==============================================================================
void loop() {
  // CRITICAL: pox.update() MUST be called as frequently as possible!
  if (poxReady) {
    pox.update();
  }

  // Non-blocking network management
  checkWiFi();
  checkMQTT();
  if (mqttClient.connected()) {
    mqttClient.loop();
  }

  unsigned long now = millis();

  // --- A. ECG STREAMING @ 20 Hz (every 50 ms) ---
  bool leadsOff = (digitalRead(LO_PLUS_PIN) == HIGH) || (digitalRead(LO_MINUS_PIN) == HIGH);
  int ecgValue  = leadsOff ? 0 : analogRead(ECG_PIN);

  if (now - lastEcgPublish >= 50) {
    lastEcgPublish = now;
    if (mqttClient.connected()) {
      String ecgMsg = "{\"sample\":" + String(ecgValue) + ",\"leads_off\":" + (leadsOff ? "true" : "false") + "}";
      mqttClient.publish("healthguard/ecg", ecgMsg.c_str());
    }
  }

  // --- B. VITALS PUBLISH & DISPLAY @ 1 Hz (every 1000 ms) ---
  if (now - lastReportTime >= 1000) {
    lastReportTime = now;

    if (poxReady) {
      currentHR   = pox.getHeartRate();
      currentSpO2 = pox.getSpO2();
    }

    // Read DS18B20 Temperature
    if (tempSensorReady) {
      float t = tempSensor.getTempCByIndex(0);
      if (t != DEVICE_DISCONNECTED_C && t > 10.0 && t < 50.0) {
        currentTemp = t;
      }
      tempSensor.requestTemperatures();
    }

    bool fingerOn = (currentHR > 25.0 && currentSpO2 > 50.0);

    // 1. Print formatted string to Serial Monitor
    Serial.print("Heart Rate: ");
    Serial.print(currentHR, 1);
    Serial.print(" BPM  |  SpO2: ");
    Serial.print(currentSpO2, 1);
    Serial.print(" %  |  Temp: ");
    Serial.print(currentTemp, 1);
    Serial.print(" C  |  WiFi: ");
    Serial.print(WiFi.status() == WL_CONNECTED ? "OK" : "NO");
    Serial.print("  |  MQTT: ");
    Serial.println(mqttClient.connected() ? "OK" : "NO");

    // 2. Prepare JSON payload for Dashboard & Edge Gateway
    String status = "ONLINE (";
    status += fingerOn ? "FINGER:YES" : "FINGER:NO";
    status += leadsOff ? "+ECG:LEADS_OFF" : "+ECG:OK";
    status += tempSensorReady ? "+TEMP:OK" : "+TEMP:DISCONNECTED";
    status += ")";

    float sendHR   = fingerOn ? currentHR : 0.0;
    float sendSpO2 = fingerOn ? currentSpO2 : 0.0;

    String payload = "{";
    payload += "\"patient_id\":\"" + String(PATIENT_ID) + "\",";
    payload += "\"heart_rate\":" + String(sendHR, 1) + ",";
    payload += "\"spo2\":" + String(sendSpO2, 1) + ",";
    payload += "\"temperature\":" + String(currentTemp, 2) + ",";
    payload += "\"finger_detected\":" + String(fingerOn ? "true" : "false") + ",";
    payload += "\"sensor_status\":\"" + status + "\",";
    payload += "\"timestamp\":" + String(now / 1000.0, 2);
    payload += "}";

    // Also output JSON for USB bridge
    Serial.print("[JSON] ");
    Serial.println(payload);

    // Publish to Raspberry Pi 5 Gateway over MQTT
    if (mqttClient.connected()) {
      mqttClient.publish("healthguard/vitals", payload.c_str());
    }
  }
}
