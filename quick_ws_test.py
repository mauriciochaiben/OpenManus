import asyncio
import sys

import websockets


async def test_ws():
    client_id = "test-client-123"
    url = f"ws://localhost:8000/api/v2/chat/ws/{client_id}"
    print(f"Testing: {url}")

    try:
        async with websockets.connect(url) as ws:
            print("✅ Connection successful!")
            await ws.send('{"type": "test", "message": "hello"}')
            print("📤 Message sent")
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                print(f"📨 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response (expected)")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_ws())
