import paramiko
import sys
import os

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    c.connect('192.168.137.245', port=22, username='rpi', password='rpi', timeout=5)
except Exception as e:
    print(f"Cannot connect to Raspberry Pi 5: {e}")
    sys.exit(1)

print("=== METHOD 2: LISTENING LIVE ON RASPBERRY PI 5 (healthguard/#) ===")
print("Listening for incoming sensor packets (10-second capture window)...")
sys.stdout.flush()

# Run mosquitto_sub for 10 seconds
cmd = "timeout 10 mosquitto_sub -t 'healthguard/#' -v"
stdin, stdout, stderr = c.exec_command(cmd)

lines = []
for line in stdout:
    l = line.strip()
    if l:
        print(f"-> {l}")
        sys.stdout.flush()
        lines.append(l)

if not lines:
    print("\n[INFO] No MQTT packets were received during this 10-second test window.")
    print("Check:")
    print("1. Is your ESP32 powered on?")
    print("2. Is your ESP32 connected to the same network, or plugged into the laptop via USB?")
else:
    print(f"\n[SUCCESS] Captured {len(lines)} live MQTT messages on the Raspberry Pi 5!")

c.close()
