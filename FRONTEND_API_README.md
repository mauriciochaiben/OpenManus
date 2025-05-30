# OpenManus Frontend API

This FastAPI backend provides the REST API and WebSocket services for the OpenManus AI Assistant frontend application.

## 🚀 Features

- **Task Management**: Create, monitor, and manage AI assistant tasks
- **Document Processing**: Upload, process, and manage documents
- **MCP Server Integration**: Configure and manage Model Context Protocol servers
- **Real-time Updates**: WebSocket support for live task progress updates
- **Multi-agent Coordination**: Support for single and multi-agent task execution
- **Complexity Analysis**: Automatic task complexity assessment

## 📋 API Endpoints

### Health & System
- `GET /health` - Health check
- `GET /info` - System information
- `GET /agents` - Available agents

### Tasks
- `POST /tasks` - Create new task
- `GET /tasks` - List all tasks
- `GET /tasks/{task_id}` - Get specific task
- `DELETE /tasks/{task_id}` - Delete task
- `POST /tasks/{task_id}/cancel` - Cancel task
- `POST /tasks/{task_id}/retry` - Retry failed task
- `GET /tasks/{task_id}/logs` - Get task logs
- `POST /analyze-complexity` - Analyze task complexity

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/{doc_id}` - Get document info
- `DELETE /documents/{doc_id}` - Delete document
- `POST /documents/{doc_id}/process` - Process document
- `GET /documents/{doc_id}/download` - Download document

### MCP Servers
- `GET /mcp/servers` - List MCP servers
- `POST /mcp/servers` - Create MCP server
- `PUT /mcp/servers/{server_id}` - Update MCP server
- `DELETE /mcp/servers/{server_id}` - Delete MCP server
- `POST /mcp/servers/{server_id}/connect` - Connect to server
- `POST /mcp/servers/{server_id}/disconnect` - Disconnect from server
- `GET /mcp/servers/{server_id}/tools` - Get server tools

### WebSocket
- `WS /ws/{client_id}` - WebSocket connection for real-time updates

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python frontend_api.py
```

The backend will start on `http://localhost:8000`.

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start on `http://localhost:3000` (or next available port).

### Quick Start (Both Services)
```bash
# Make executable and run
chmod +x start_dev.sh
./start_dev.sh
```

## 📊 Data Models

### Task
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "complexity": "low|medium|high",
  "priority": "low|medium|high|urgent",
  "mode": "auto|single|multi",
  "status": "pending|running|completed|error|cancelled",
  "progress": 0.0,
  "created_at": "2025-05-29T22:00:00",
  "documents": [],
  "tags": [],
  "steps": []
}
```

### Document
```json
{
  "id": "string",
  "filename": "string",
  "file_size": 1024,
  "file_type": "text/plain",
  "status": "uploaded|processing|processed|error",
  "uploaded_at": "2025-05-29T22:00:00"
}
```

### MCP Server
```json
{
  "id": "string",
  "name": "string",
  "host": "localhost",
  "port": 8001,
  "enabled": true,
  "status": "connected|disconnected|error",
  "tools": []
}
```

## 🔄 WebSocket Events

The WebSocket connection provides real-time updates for:

- `task_created` - New task created
- `task_started` - Task execution started
- `task_completed` - Task completed
- `task_cancelled` - Task cancelled
- `task_error` - Task error occurred
- `step_started` - Task step started
- `step_completed` - Task step completed
- `progress_update` - Progress update

## 🧪 Testing

Test the API endpoints:

```bash
# Health check
curl http://localhost:8000/health

# List tasks
curl http://localhost:8000/tasks

# Create task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Test description",
    "complexity": "medium",
    "priority": "high"
  }'

# Upload document
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@document.txt"
```

## 📁 File Structure

```
/Users/mauriciochaiben/OpenManus/
├── frontend_api.py          # Main FastAPI application
├── start_dev.sh            # Development startup script
├── requirements.txt        # Python dependencies
├── uploads/               # Uploaded documents storage
└── frontend/              # React frontend application
    ├── src/
    │   ├── components/    # React components
    │   ├── services/      # API and WebSocket services
    │   ├── types/         # TypeScript type definitions
    │   └── pages/         # Application pages
    └── package.json       # Frontend dependencies
```

## 🔧 Configuration

### Environment Variables
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)
- `VITE_WS_BASE_URL`: WebSocket URL (default: http://localhost:8000)

### CORS Configuration
The backend allows requests from:
- `http://localhost:3000` (React dev server default)
- `http://localhost:5173` (Vite dev server default)

## 📈 Features in Development

- [ ] Database integration (PostgreSQL/SQLite)
- [ ] Authentication and user management
- [ ] File storage optimization
- [ ] Advanced task scheduling
- [ ] Integration with actual MCP servers
- [ ] Enhanced document processing
- [ ] Task templates and presets

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   - Backend: Change port in `frontend_api.py`
   - Frontend: Vite will automatically find next available port

2. **CORS errors**
   - Ensure frontend URL is in CORS allowed origins
   - Check browser developer tools for specific errors

3. **File upload issues**
   - Ensure `python-multipart` is installed
   - Check `uploads/` directory permissions

4. **WebSocket connection failed**
   - Verify backend is running on correct port
   - Check browser WebSocket support

### Logs
- Backend logs: Check terminal output where `python frontend_api.py` is running
- Frontend logs: Check browser developer console
- File uploads: Check `uploads/` directory

## 📚 API Documentation

When the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is part of the OpenManus AI Assistant system.
