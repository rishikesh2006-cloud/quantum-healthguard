"""
Quantum HealthGuard — Pure Python MQTT Broker
Uses the 'amqtt' library (no Mosquitto installation required on Windows)
Run this FIRST before simulator and receiver
"""

import asyncio
from amqtt.broker import Broker

config = {
    "listeners": {
        "default": {
            "type": "tcp",
            "bind": "0.0.0.0:1883",
        }
    },
    "sys_interval": 10,
    "auth": {
        "allow-anonymous": True,
    },
    "topic-check": {
        "enabled": False,
    },
}

broker = Broker(config)

async def main():
    print("=" * 50)
    print("  Quantum HealthGuard — MQTT Broker")
    print("  Listening on localhost:1883")
    print("  Press Ctrl+C to stop.")
    print("=" * 50)
    await broker.start()
    try:
        await asyncio.sleep(float("inf"))
    except asyncio.CancelledError:
        pass
    finally:
        await broker.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[BROKER] Stopped.")
