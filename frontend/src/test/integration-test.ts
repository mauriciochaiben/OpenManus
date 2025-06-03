// Quick integration test for WebSocket and EventBus system
import { webSocketManager } from "../services/websocket";
import { eventBus } from "../utils/eventBus";

// Test WebSocket initialization
console.log("Testing WebSocket and EventBus integration...");

// Initialize WebSocket (won't actually connect without server)
webSocketManager.initialize("ws://localhost:8000/ws");

// Test EventBus
eventBus.on("test:message", (data) => {
  console.log("Received test message:", data);
});

eventBus.emit("test:message", { message: "Hello from EventBus!" });

// Test connection state
console.log(
  "WebSocket connection state:",
  webSocketManager.getConnectionState(),
);
console.log("WebSocket is connected:", webSocketManager.isConnected());

console.log("✅ Integration test completed successfully");
