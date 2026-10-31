"""
Automated Deployment Script for Raspberry Pi 5 Edge Computing Node
Quantum HealthGuard — Stage 2: Edge Processor & MQTT Gateway
"""

import sys
import os
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")

import paramiko
import time

RPI_IP = "192.168.137.245"
RPI_USER = "rpi"
RPI_PASS = "rpi"

print(f"Connecting to Raspberry Pi 5 at {RPI_IP}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(RPI_IP, port=22, username=RPI_USER, password=RPI_PASS, timeout=10)
    print("SSH Connection Established Successfully!")
except Exception as e:
    print(f"Connection Failed: {e}")
    sys.exit(1)

def run_cmd(cmd, sudo=False):
    print(f"\n[RPI EXEC] {cmd}")
    full_cmd = f"echo {RPI_PASS} | sudo -S bash -c '{cmd}'" if sudo else cmd
    stdin, stdout, stderr = client.exec_command(full_cmd)
    
    while True:
        line = stdout.readline()
        if not line:
            break
        try:
            print(line.rstrip())
        except Exception:
            pass
        
    err = stderr.read().decode("utf-8", errors="replace").strip()
    filtered_err = "\n".join([l for l in err.splitlines() if "password for" not in l and "WARNING: apt does not" not in l])
    if filtered_err:
        print(f"[RPI STDERR] {filtered_err}")

# 2. Configure Mosquitto for external network listening
print("\n--- 2. Configuring Mosquitto for Port 1883 ---")
run_cmd("""cat << 'EOF' > /etc/mosquitto/conf.d/healthguard.conf
listener 1883 0.0.0.0
allow_anonymous true
EOF""", sudo=True)

run_cmd("systemctl restart mosquitto", sudo=True)
run_cmd("systemctl enable mosquitto", sudo=True)
run_cmd("systemctl is-active mosquitto")

# 3. Clone or pull latest Quantum HealthGuard repository on Pi
print("\n--- 3. Deploying Quantum HealthGuard repository to Pi 5 ---")
run_cmd("""
if [ -d "$HOME/QuantumHealthGuard/.git" ]; then
    cd $HOME/QuantumHealthGuard && git pull origin master
else
    rm -rf $HOME/QuantumHealthGuard
    git clone https://github.com/rishikesh2006-cloud/quantum-healthguard.git $HOME/QuantumHealthGuard
fi
""")

# 4. Create Edge systemd service to run Stage 2 Edge Processor automatically
print("\n--- 4. Creating and starting healthguard-edge.service ---")
run_cmd("""cat << 'EOF' > /etc/systemd/system/healthguard-edge.service
[Unit]
Description=Quantum HealthGuard Stage 2 Edge Processor
After=network.target mosquitto.service

[Service]
Type=simple
User=rpi
WorkingDirectory=/home/rpi/QuantumHealthGuard
ExecStart=/usr/bin/python3 /home/rpi/QuantumHealthGuard/communication/mqtt_receiver.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF""", sudo=True)

run_cmd("systemctl daemon-reload", sudo=True)
run_cmd("systemctl enable healthguard-edge.service", sudo=True)
run_cmd("systemctl restart healthguard-edge.service", sudo=True)
time.sleep(2)
run_cmd("systemctl status healthguard-edge.service --no-pager | head -n 15", sudo=True)

client.close()
print("\n=== RASPBERRY PI 5 EDGE COMPUTING DEPLOYMENT COMPLETE! ===")
