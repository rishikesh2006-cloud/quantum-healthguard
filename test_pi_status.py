import paramiko
import sys

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    c.connect('192.168.137.245', port=22, username='rpi', password='rpi', timeout=5)
except Exception as e:
    print("SSH FAILED:", e)
    sys.exit(1)

def run(cmd):
    stdin, stdout, stderr = c.exec_command(cmd)
    out = stdout.read().decode('ascii', errors='replace').strip()
    err = stderr.read().decode('ascii', errors='replace').strip()
    print(f"=== {cmd} ===")
    if out: print(out)
    if err: print("ERR:", err)

run("systemctl is-active mosquitto")
run("systemctl is-active healthguard-edge.service")
run("python3 -c 'import flask; print(flask.__file__)'")
run("ls -la /home/rpi/QuantumHealthGuard")
run("journalctl -u healthguard-edge.service -n 5 --no-pager")
c.close()
