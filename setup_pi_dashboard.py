import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.137.245', port=22, username='rpi', password='rpi', timeout=10)

def run(cmd):
    full = f"echo rpi | sudo -S bash -c \"{cmd}\""
    stdin, stdout, stderr = c.exec_command(full)
    for l in stdout:
        print(l.rstrip())

# Create healthguard-dashboard.service on the Pi 5
run("""cat << 'EOF' > /etc/systemd/system/healthguard-dashboard.service
[Unit]
Description=Quantum HealthGuard Dashboard Server
After=network.target mosquitto.service healthguard-edge.service

[Service]
Type=simple
User=rpi
WorkingDirectory=/home/rpi/QuantumHealthGuard
ExecStart=/usr/bin/python3 /home/rpi/QuantumHealthGuard/dashboard/app.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF""")

run("systemctl daemon-reload")
run("systemctl enable healthguard-dashboard.service")
run("systemctl restart healthguard-dashboard.service")
run("systemctl status healthguard-dashboard.service --no-pager | head -n 12")

c.close()
print("DASHBOARD_SERVICE_CONFIGURED_ON_PI")
