"""
Quantum HealthGuard -- Pure Python MQTT Broker
Uses the 'amqtt' library (no Mosquitto installation required on Windows)
Run this FIRST before simulator and receiver.
"""

import asyncio
import logging
import sys
import os

# Fix Windows console encoding for Python 3.13+
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

logging.basicConfig(level=logging.ERROR)  # suppress amqtt verbose logs

BROKER_CONFIG = {
    "listeners": {
        "default": {
            "type": "tcp",
            "bind": "0.0.0.0:1883",
        }
    },
    "sys_interval": 0,
    "auth": {
        "allow-anonymous": True,
        "plugins": [],
    },
    "topic-check": {
        "enabled": False,
    },
}


async def run_broker():
    from amqtt.broker import Broker
    broker = Broker(BROKER_CONFIG)
    await broker.start()
    print("=" * 50)
    print("  Quantum HealthGuard -- MQTT Broker")
    print("  Listening on localhost:1883  [OK]")
    print("  Press Ctrl+C to stop.")
    print("=" * 50)
    sys.stdout.flush()
    try:
        await asyncio.sleep(float("inf"))
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
    finally:
        await broker.shutdown()
        print("[BROKER] Stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(run_broker())
    except KeyboardInterrupt:
        print("\n[BROKER] Stopped.")
    except OSError as e:
        if "10048" in str(e) or "Address already in use" in str(e):
            print("[BROKER] Port 1883 already in use -- another broker may already be running. That is OK!")
            sys.exit(0)
        raise
