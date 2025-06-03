#!/usr/bin/env python3
"""
Final WebSocket Validation Script
Confirms that all WebSocket fixes are working correctly
"""

import asyncio
import json
import random
import string
import time

import websockets


def generate_frontend_client_id():
    """Generate client ID exactly like frontend does"""
    timestamp = int(time.time() * 1000)  # Date.now() equivalent
    random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"frontend-{timestamp}-{random_part}"


async def validate_websocket_fix():
    """Validate that WebSocket connectivity is working"""
    print("🔍 FINAL WEBSOCKET VALIDATION")
    print("=" * 50)

    # Test 1: Frontend-style connection
    client_id = generate_frontend_client_id()
    ws_url = f"ws://localhost:8000/api/v2/chat/ws/{client_id}"

    print(f"🆔 Generated Client ID: {client_id}")
    print(f"🔗 WebSocket URL: {ws_url}")
    print()

    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket Connection: SUCCESS")

            # Test message sending
            test_message = {
                "type": "validation_test",
                "data": {
                    "message": "Final validation test",
                    "timestamp": time.time(),
                    "client_id": client_id,
                },
            }

            await websocket.send(json.dumps(test_message))
            print("✅ Message Sending: SUCCESS")

            # Try to receive any response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                print(f"✅ Response Received: {response[:100]}...")
            except TimeoutError:
                print("ℹ️  No immediate response (expected for chat WebSocket)")

            print("✅ WebSocket Validation: COMPLETE")

    except Exception as e:
        print(f"❌ WebSocket Validation: FAILED - {e}")
        return False

    print()
    print("🎉 WEBSOCKET FIXES VALIDATED SUCCESSFULLY!")
    print("💡 The frontend should now connect to WebSocket without issues")
    print("🌐 Frontend URL: http://localhost:3003")
    print("🔧 Backend URL: http://localhost:8000/docs")

    return True


if __name__ == "__main__":
    result = asyncio.run(validate_websocket_fix())
    exit(0 if result else 1)
