#!/usr/bin/env python3
"""
Test script to verify the frontend WebSocket connection works with dynamic client_id
This simulates the frontend connection with the same format used in main.tsx
"""
import asyncio
import json
import random
import string
import time

import websockets


def generate_client_id():
    """Generate a client ID using the same format as frontend"""
    timestamp = int(time.time() * 1000)  # milliseconds like Date.now()
    random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"frontend-{timestamp}-{random_part}"


async def test_frontend_websocket():
    """Test WebSocket connection with frontend-style client_id"""
    client_id = generate_client_id()
    ws_url = f"ws://localhost:8000/api/v2/chat/ws/{client_id}"

    print(f"🔗 Testing WebSocket connection to: {ws_url}")
    print(f"📱 Client ID: {client_id}")

    try:
        # Connect to WebSocket
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully!")

            # Send a test message (simulating frontend behavior)
            test_message = {
                "type": "chat_message",
                "data": {
                    "message": "Hello from frontend simulation!",
                    "timestamp": time.time(),
                },
            }

            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message: {test_message}")

            # Wait for response (if any)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Received response: {response}")
            except asyncio.TimeoutError:
                print(
                    "⏰ No response received within 5 seconds (this is expected for chat WebSocket)"
                )

            # Send a ping to test heartbeat
            ping_message = {"type": "ping", "data": {}}
            await websocket.send(json.dumps(ping_message))
            print("💓 Sent ping message")

            # Wait for pong
            try:
                pong_response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"🏓 Received pong: {pong_response}")
            except asyncio.TimeoutError:
                print("⏰ No pong received (backend might not implement ping/pong)")

            print("✅ WebSocket test completed successfully!")

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🚀 OpenManus Frontend WebSocket Test")
    print("=" * 50)

    # Test single connection
    single_success = asyncio.run(test_frontend_websocket())

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Single Connection: {'✅ PASS' if single_success else '❌ FAIL'}")

    if single_success:
        print("🎉 WebSocket test passed! Frontend connection should work.")
    else:
        print("⚠️ Test failed. Check the backend WebSocket implementation.")
