#!/usr/bin/env python3
"""
Simple test script for progress broadcasting functionality
"""

import asyncio
import json
import logging
from datetime import datetime

import requests
import websockets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_websocket_and_progress():
    """Test WebSocket connection and progress broadcasting"""

    # Test basic backend health
    logger.info("1. Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        logger.info(f"Backend health: {response.json()}")
    except Exception as e:
        logger.error(f"Backend health check failed: {e}")
        return

    # Test WebSocket connection and progress
    logger.info("2. Testing WebSocket connection and progress broadcasting...")

    client_id = f"test-client-{int(datetime.now().timestamp())}"
    websocket_url = f"ws://localhost:8000/api/v2/chat/ws/{client_id}"

    try:
        async with websockets.connect(websocket_url) as websocket:
            logger.info(f"Connected to WebSocket: {websocket_url}")

            # Send a simple message to trigger multi-agent flow
            test_message = {
                "type": "chat_message",
                "content": "Teste simples para verificar progresso",
                "timestamp": datetime.now().isoformat(),
            }

            await websocket.send(json.dumps(test_message))
            logger.info("Sent test message to trigger processing")

            # Listen for responses for a limited time
            progress_messages = []
            timeout_count = 0
            max_timeout = 10  # 10 second timeout

            while timeout_count < max_timeout:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    logger.info(f"Received message type: {data.get('type')}")

                    if data.get("type") == "task_progress":
                        progress_messages.append(data)
                        logger.info(
                            f"Progress: {data.get('progress', 0)}% - {data.get('stage', 'Unknown')}"
                        )
                        logger.info(f"Details: {data}")
                    elif data.get("type") == "task_completed":
                        logger.info("Task completed!")
                        logger.info(f"Completion details: {data}")
                        break
                    elif data.get("type") == "task_failed":
                        logger.info("Task failed!")
                        logger.info(f"Failure details: {data}")
                        break
                    elif data.get("type") == "chat_response":
                        logger.info("Received chat response")
                        logger.info(f"Response: {data.get('content', '')[:100]}...")
                    else:
                        logger.info(f"Other message: {data}")

                except asyncio.TimeoutError:
                    timeout_count += 1
                    logger.info(
                        f"Waiting for messages... ({timeout_count}/{max_timeout})"
                    )
                    continue
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                    continue

            logger.info(
                f"Test completed. Received {len(progress_messages)} progress messages."
            )

            if progress_messages:
                logger.info("Progress messages summary:")
                for i, msg in enumerate(progress_messages):
                    logger.info(
                        f"  {i+1}. {msg.get('progress', 0)}% - {msg.get('stage', 'Unknown')}"
                    )
            else:
                logger.warning(
                    "No progress messages received. This might indicate the progress broadcasting is not working."
                )

    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket_and_progress())
