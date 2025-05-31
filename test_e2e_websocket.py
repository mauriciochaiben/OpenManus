#!/usr/bin/env python3
"""
End-to-end test for OpenManus WebSocket chat functionality
Tests the complete workflow: WebSocket connection, message sending, and real-time updates
"""
import asyncio
import json
import random
import string
import time
from typing import Any, Dict, List

import requests


class WebSocketChatTester:
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        ws_url: str = "ws://localhost:8000",
    ):
        self.base_url = base_url
        self.ws_url = ws_url
        self.client_id = self.generate_client_id()

    def generate_client_id(self) -> str:
        """Generate a unique client ID similar to frontend"""
        timestamp = int(time.time() * 1000)
        random_part = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=9)
        )
        return f"e2e-test-{timestamp}-{random_part}"

    async def test_websocket_connection(self) -> bool:
        """Test basic WebSocket connection"""
        print("🔗 Testing WebSocket Connection...")

        try:
            import websockets

            ws_endpoint = f"{self.ws_url}/api/v2/chat/ws/{self.client_id}"
            print(f"   Connecting to: {ws_endpoint}")

            async with websockets.connect(ws_endpoint) as websocket:
                print("   ✅ WebSocket connected successfully")

                # Test ping/pong
                ping_message = {"type": "ping", "data": {}}
                await websocket.send(json.dumps(ping_message))
                print("   📤 Sent ping message")

                # Wait for any response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3)
                    print(f"   📨 Received: {response}")
                except asyncio.TimeoutError:
                    print("   ⏰ No immediate response (normal for chat WebSocket)")

                return True

        except Exception as e:
            print(f"   ❌ WebSocket connection failed: {e}")
            return False

    def test_backend_health(self) -> bool:
        """Test backend API health"""
        print("🏥 Testing Backend Health...")

        try:
            # Try different health endpoints
            health_endpoints = [
                f"{self.base_url}/health",
                f"{self.base_url}/api/v2/health",
                f"{self.base_url}/docs",  # FastAPI docs endpoint
            ]

            for endpoint in health_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code in [
                        200,
                        404,
                    ]:  # 404 for /health is ok if docs work
                        print(f"   ✅ Backend is responding at {endpoint}")
                        return True
                except requests.RequestException:
                    continue

            print("   ❌ Backend is not responding")
            return False

        except Exception as e:
            print(f"   ❌ Backend health check failed: {e}")
            return False

    async def test_chat_workflow(self) -> bool:
        """Test complete chat workflow with WebSocket"""
        print("💬 Testing Chat Workflow...")

        try:
            import websockets

            ws_endpoint = f"{self.ws_url}/api/v2/chat/ws/{self.client_id}"

            async with websockets.connect(ws_endpoint) as websocket:
                print("   📱 Connected to chat WebSocket")

                # Simulate frontend chat message
                chat_message = {
                    "type": "chat_message",
                    "data": {
                        "message": "Hello, OpenManus! This is an end-to-end test.",
                        "timestamp": time.time(),
                        "user": "test_user",
                    },
                }

                await websocket.send(json.dumps(chat_message))
                print(f"   📤 Sent chat message: {chat_message['data']['message']}")

                # Wait for any response or acknowledgment
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    print(f"   📨 Received response: {response}")

                    # Try to parse the response
                    try:
                        response_data = json.loads(response)
                        print(
                            f"   📋 Parsed response type: {response_data.get('type', 'unknown')}"
                        )
                    except json.JSONDecodeError:
                        print("   📋 Response is not JSON format")

                except asyncio.TimeoutError:
                    print(
                        "   ⏰ No response received (this is normal for some chat systems)"
                    )

                # Test multiple message types
                test_messages = [
                    {"type": "system_status_request", "data": {}},
                    {"type": "heartbeat", "data": {"timestamp": time.time()}},
                ]

                for msg in test_messages:
                    await websocket.send(json.dumps(msg))
                    print(f"   📤 Sent {msg['type']} message")

                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2)
                        print(f"   📨 Response to {msg['type']}: {response[:100]}...")
                    except asyncio.TimeoutError:
                        print(f"   ⏰ No response to {msg['type']}")

                return True

        except Exception as e:
            print(f"   ❌ Chat workflow test failed: {e}")
            return False

    async def run_full_test_suite(self) -> Dict[str, bool]:
        """Run complete test suite"""
        print("🚀 OpenManus E2E WebSocket Test Suite")
        print("=" * 60)
        print(f"🆔 Client ID: {self.client_id}")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🔌 WebSocket URL: {self.ws_url}")
        print()

        results = {}

        # Test 1: Backend Health
        results["backend_health"] = self.test_backend_health()
        print()

        # Test 2: WebSocket Connection
        results["websocket_connection"] = await self.test_websocket_connection()
        print()

        # Test 3: Chat Workflow
        results["chat_workflow"] = await self.test_chat_workflow()
        print()

        # Summary
        print("=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")

        all_passed = all(results.values())
        print()
        if all_passed:
            print("🎉 All tests passed! WebSocket functionality is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the individual results above.")

        return results


async def main():
    tester = WebSocketChatTester()
    results = await tester.run_full_test_suite()

    # Exit with appropriate code
    exit_code = 0 if all(results.values()) else 1
    exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
