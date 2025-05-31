<p align="center">
  <img src="assets/logo.jpg" width="200"/>
</p>

English | [中文](README_zh.md) | [한국어](README_ko.md) | [日本語](README_ja.md)

[![GitHub stars](https://img.shields.io/github/stars/mannaandpoem/OpenManus?style=social)](https://github.com/mannaandpoem/OpenManus/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &ensp;
[![Discord Follow](https://dcbadge.vercel.app/api/server/DYn29wFk9z?style=flat)](https://discord.gg/DYn29wFk9z)
[![Demo](https://img.shields.io/badge/Demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/lyh-917/OpenManusDemo)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15186407.svg)](https://doi.org/10.5281/zenodo.15186407)

# 👋 OpenManus

Manus is incredible, but OpenManus can achieve any idea without an *Invite Code* 🛫!

Our team members [@Xinbin Liang](https://github.com/mannaandpoem) and [@Jinyu Xiang](https://github.com/XiangJinyu) (core authors), along with [@Zhaoyang Yu](https://github.com/MoshiQAQ), [@Jiayi Zhang](https://github.com/didiforgithub), and [@Sirui Hong](https://github.com/stellaHSR), we are from [@MetaGPT](https://github.com/geekan/MetaGPT). The prototype is launched within 3 hours and we are keeping building!

It's a simple implementation, so we welcome any suggestions, contributions, and feedback!

Enjoy your own agent with OpenManus!

We're also excited to introduce [OpenManus-RL](https://github.com/OpenManus/OpenManus-RL), an open-source project dedicated to reinforcement learning (RL)- based (such as GRPO) tuning methods for LLM agents, developed collaboratively by researchers from UIUC and OpenManus.

## 🏗️ Architecture Overview

OpenManus features a complete **5-pillar enterprise-grade architecture**:

### ✅ **Pillar 1: Backend Architecture**
- **Clean Architecture** with Domain-Driven Design (DDD)
- **FastAPI** with structured controllers, services, and repositories
- **Type-safe** Python with comprehensive error handling
- **API versioning** and standardized response patterns

### ✅ **Pillar 2: Frontend Architecture**
- **Feature-based structure** with React + TypeScript + Vite
- **Zustand** for predictable state management
- **Ant Design** components for consistent UI/UX
- **Modular component architecture** with hooks and contexts

### ✅ **Pillar 3: Communication System**
- **RobustWebSocket** with automatic reconnection and retry logic
- **Typed EventBus** for real-time updates between frontend and backend
- **Event-driven architecture** for task execution and system notifications
- **Connection state management** with graceful degradation

### ✅ **Pillar 4: Testing Strategy**
- **Test factories** for consistent mock data generation
- **Jest** configuration for React component testing
- **End-to-End (E2E)** test structure with Playwright
- **Type-safe test utilities** and comprehensive coverage

### ✅ **Pillar 5: DevOps & Deployment**
- **Docker containerization** for consistent development environments
- **Automated setup scripts** for quick project bootstrapping
- **CI/CD ready** configuration with development and production modes
- **Environment-based configuration** management

### 🔧 **Key Technical Features:**
- **Real-time WebSocket communication** for live task updates
- **Event-driven notifications** system for user feedback
- **Type-safe data flow** from database to UI components
- **Graceful error handling** and connection recovery
- **Scalable project structure** ready for enterprise deployment

## Project Demo

<video src="https://private-user-images.githubusercontent.com/61239030/420168772-6dcfd0d2-9142-45d9-b74e-d10aa75073c6.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDEzMTgwNTksIm5iZiI6MTc0MTMxNzc1OSwicGF0aCI6Ii82MTIzOTAzMC80MjAxNjg3NzItNmRjZmQwZDItOTE0Mi00NWQ5LWI3NGUtZDEwYWE3NTA3M2M2Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMDclMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzA3VDAzMjIzOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTdiZjFkNjlmYWNjMmEzOTliM2Y3M2VlYjgyNDRlZDJmOWE3NWZhZjE1MzhiZWY4YmQ3NjdkNTYwYTU5ZDA2MzYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.UuHQCgWYkh0OQq9qsUWqGsUbhG3i9jcZDAMeHjLt5T4" data-canonical-src="https://private-user-images.githubusercontent.com/61239030/420168772-6dcfd0d2-9142-45d9-b74e-d10aa75073c6.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDEzMTgwNTksIm5iZiI6MTc0MTMxNzc1OSwicGF0aCI6Ii82MTIzOTAzMC80MjAxNjg3NzItNmRjZmQwZDItOTE0Mi00NWQ5LWI3NGUtZDEwYWE3NTA3M2M2Lm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAzMDclMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMzA3VDAzMjIzOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTdiZjFkNjlmYWNjMmEzOTliM2Y3M2VlYjgyNDRlZDJmOWE3NWZhZjE1MzhiZWY4YmQ3NjdkNTYwYTU5ZDA2MzYmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.UuHQCgWYkh0OQq9qsUWqGsUbhG3i9jcZDAMeHjLt5T4" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px"></video>

## Installation

We provide a streamlined installation process. The **Quick Start** method is recommended for the best experience.

### 🚀 Quick Start (Recommended)

The easiest way to get OpenManus running with both frontend and backend:

1. Clone the repository:
```bash
git clone https://github.com/mauriciochaiben/OpenManus.git
cd OpenManus
```

2. Run the development setup:
```bash
./start_dev.sh
```

This script will automatically:
- ✅ Check system dependencies (Python, Node.js)
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Start both frontend and backend services

**That's it!** Your OpenManus instance will be running with:
- 🌐 Frontend: http://localhost:3000
- 📡 Backend API: http://localhost:8000
- 📚 API Documentation: http://localhost:8000/docs

### 🐍 Manual Setup

If you prefer manual setup:

1. Clone and create environment:
```bash
git clone https://github.com/mauriciochaiben/OpenManus.git
cd OpenManus
python3 -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# Or on Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

3. Start services:
```bash
npm run dev
```

For conda users:

```bash
conda create -n open_manus python=3.12
conda activate open_manus
git clone https://github.com/mannaandpoem/OpenManus.git
cd OpenManus
pip install -r requirements.txt
```

## Configuration

OpenManus requires configuration for the LLM APIs it uses. The automated setup creates this for you, but you can also configure manually:

### 🔧 Automated Configuration

If you used the automated setup (`./setup_openmanus.sh`), the configuration file is automatically created at `config/config.toml`. You just need to add your API keys.

### 🛠️ Manual Configuration

1. Create the configuration file:
```bash
cp config/examples/config.example.toml config/config.toml
```

2. Edit `config/config.toml` to add your API keys and customize settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
max_tokens = 4096
temperature = 0.0

# Optional configuration for specific LLM models
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
```

### 🗝️ Supported API Providers

OpenManus supports multiple LLM providers:
- **OpenAI** (GPT-4, GPT-4o, etc.)
- **Anthropic** (Claude 3.5 Sonnet, etc.)
- **Azure OpenAI**
- **AWS Bedrock**
- **Ollama** (Local models)

See `config/examples/config.example.toml` for configuration examples for each provider.

## Quick Start

### 🚀 Complete Application (Frontend + Backend)

If you used the automated setup:

```bash
./dev.sh
```

Or using the existing development script:

```bash
./start_dev.sh
```

This will start:
- 🌐 **Frontend**: http://localhost:3000 (React application)
- 📡 **Backend**: http://localhost:8000 (FastAPI server)
- 📚 **API Docs**: http://localhost:8000/docs (OpenAPI documentation)

### 🐍 Backend Only

## Usage

### 🚀 Running OpenManus

After installation, you can use OpenManus in several ways:

#### Web Interface (Recommended)
After running `./start_dev.sh`, access the web interface at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

#### Command Line Interface
For terminal-based interaction:

```bash
python main.py
```

#### MCP Server Mode
For Model Context Protocol tools:
```bash
python run_mcp_server.py
```

## Project Structure

```
OpenManus/
├── 📱 frontend/          # React frontend application
├── 🐍 app/              # Python backend application
│   ├── agent/          # AI agent implementations
│   ├── api/            # FastAPI routes and controllers
│   ├── flow/           # Multi-agent workflows
│   ├── mcp/            # Model Context Protocol server
│   ├── services/       # Business logic services
│   └── tool/           # Tools and utilities
├── ⚙️ config/           # Configuration files
├── 📚 docs/             # Documentation
├── 🧪 tests/            # Test suite
├── 📄 scripts/          # Utility scripts
├── 📄 main.py           # Main CLI application
├── 🚀 start_dev.sh      # Development launcher
└── 📚 README.md         # This file
```

## 🔧 Development Guide

### Getting Started with Development

1. **Complete Setup**: Run the automated setup first
   ```bash
   ./setup_openmanus.sh
   ```

2. **Start Development Environment**:
   ```bash
   ./dev.sh
   ```

3. **VS Code Integration**: If using VS Code, you can use the built-in task:
   - Open Command Palette (`Cmd+Shift+P`)
   - Run "Tasks: Run Task"
   - Select "start-openmanus-dev"

### 🧪 Running Tests

The project includes comprehensive tests for both backend and frontend:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all backend tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_basic_functionality.py -v
python -m pytest tests/test_multi_agent.py -v
python -m pytest tests/sandbox/ -v

# Frontend tests (if dependencies are installed)
cd frontend && npm test
```

### 📁 Project Architecture

```
OpenManus/
├── 🌐 Frontend (React + TypeScript)
│   ├── src/components/     # React components
│   ├── src/pages/         # Page components
│   ├── src/services/      # API services
│   └── src/types/         # TypeScript definitions
│
├── 🐍 Backend (FastAPI + Python)
│   ├── app/agent/         # AI agent implementations
│   │   ├── manus.py       # Main agent class
│   │   ├── decision.py    # Multi-agent decision system
│   │   └── browser.py     # Browser automation agent
│   ├── app/flow/          # Multi-agent workflows
│   ├── app/sandbox/       # Secure code execution
│   ├── app/tool/          # Tools and utilities
│   └── app/mcp/           # Model Context Protocol
│
├── ⚙️ Configuration
│   ├── config/config.toml # Main configuration
│   └── config/examples/   # Configuration examples
│
└── 🧪 Tests
    ├── tests/frontend/    # Frontend tests
    ├── tests/sandbox/     # Sandbox tests
    └── tests/*.py         # Backend tests
```

### 🛠️ Development Workflow

1. **Feature Development**:
   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name

   # Start development environment
   ./dev.sh

   # Make changes and test
   python -m pytest tests/ -v

   # Commit and push
   git add .
   git commit -m "feat: add your feature"
   git push origin feature/your-feature-name
   ```

2. **Debugging**:
   - Backend logs: Check `logs/` directory
   - Frontend: Use browser developer tools
   - API testing: http://localhost:8000/docs

3. **Adding New Features**:
   - Backend: Add to appropriate module in `app/`
   - Frontend: Add components in `frontend/src/`
   - Tests: Add corresponding tests in `tests/`

## How to contribute

We welcome any friendly suggestions and helpful contributions!

### 🤝 Contributing Guidelines

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/OpenManus.git
   cd OpenManus
   ./setup_openmanus.sh
   ```

2. **Development Setup**:
   - Follow the installation guide above
   - Run tests to ensure everything works
   - Create a feature branch for your changes

3. **Code Standards**:
   - Python: Follow PEP 8, use type hints
   - TypeScript: Follow project ESLint configuration
   - Add tests for new functionality
   - Update documentation as needed

4. **Pull Request Process**:
   - Ensure all tests pass
   - Run pre-commit checks: `pre-commit run --all-files`
   - Provide clear description of changes
   - Reference any related issues

5. **Areas for Contribution**:
   - 🐛 Bug fixes
   - ✨ New features
   - 📚 Documentation improvements
   - 🧪 Test coverage
   - 🌐 Internationalization
   - 🎨 UI/UX improvements

### 📞 Contact

- 📧 Email: mannaandpoem@gmail.com
- 💬 Discord: [Join our community](https://discord.gg/DYn29wFk9z)
- 🐛 Issues: [GitHub Issues](https://github.com/mannaandpoem/OpenManus/issues)

**Note**: Before submitting a pull request, please use the pre-commit tool to check your changes. Run `pre-commit run --all-files` to execute the checks.

## Community Group
Join our networking group on Feishu and share your experience with other developers!

<div align="center" style="display: flex; gap: 20px;">
    <img src="assets/community_group.jpg" alt="OpenManus 交流群" width="300" />
</div>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mannaandpoem/OpenManus&type=Date)](https://star-history.com/#mannaandpoem/OpenManus&Date)

## Sponsors
Thanks to [PPIO](https://ppinfra.com/user/register?invited_by=OCPKCN&utm_source=github_openmanus&utm_medium=github_readme&utm_campaign=link) for computing source support.
> PPIO: The most affordable and easily-integrated MaaS and GPU cloud solution.


## Acknowledgement

Thanks to [anthropic-computer-use](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
and [browser-use](https://github.com/browser-use/browser-use) for providing basic support for this project!

Additionally, we are grateful to [AAAJ](https://github.com/metauto-ai/agent-as-a-judge), [MetaGPT](https://github.com/geekan/MetaGPT), [OpenHands](https://github.com/All-Hands-AI/OpenHands) and [SWE-agent](https://github.com/SWE-agent/SWE-agent).

We also thank stepfun(阶跃星辰) for supporting our Hugging Face demo space.

OpenManus is built by contributors from MetaGPT. Huge thanks to this agent community!

## Cite
```bibtex
@misc{openmanus2025,
  author = {Xinbin Liang and Jinyu Xiang and Zhaoyang Yu and Jiayi Zhang and Sirui Hong and Sheng Fan and Xiao Tang},
  title = {OpenManus: An open-source framework for building general AI agents},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.15186407},
  url = {https://doi.org/10.5281/zenodo.15186407},
}
```
