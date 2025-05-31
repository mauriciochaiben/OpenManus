#!/usr/bin/env python3
import subprocess
import sys


# Simple manual test using netcat-like approach
def test_ws_connection():
    client_id = "manual-test-123"
    url = f"ws://localhost:8000/api/v2/chat/ws/{client_id}"
    print(f"Testing WebSocket at: {url}")

    # Use wscat if available, otherwise use Python
    try:
        result = subprocess.run(["which", "wscat"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Using wscat...")
            cmd = ["wscat", "-c", url]
            subprocess.run(cmd, timeout=5)
        else:
            print("wscat not found, testing with Python...")
            import asyncio

            import websockets

            async def connect():
                try:
                    async with websockets.connect(url) as ws:
                        print("✅ WebSocket connected!")
                        await ws.send('{"type": "test"}')
                        print("📤 Test message sent")
                        return True
                except Exception as e:
                    print(f"❌ Connection failed: {e}")
                    return False

            return asyncio.run(connect())
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_ws_connection()
