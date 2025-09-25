# Nanda Agent

A sophisticated, persona-driven AI chat system built on `crewAI`. This project provides a generic and extensible framework for creating a conversational agent that helps users craft a compelling startup pitch designed to attract its persona, Enrique, as a potential technical co-founder.

## Project Overview

## Architecture:

## System Capabilities

### Runtime Flow

## Quick Start

This project uses `uv` for dependency management and Python environment handling.

### 1. Prerequisites
- **uv**: Install from [https://docs.astral.sh/uv/getting-started/installation/#standalone-installer](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)
- **Python 3.11.11**: Tested with Python 3.11.11
- **OpenAI API key**: Required for the chat functionality

### 2. Installation
Clone the repository and install the dependencies using `uv`.

```bash
git clone <repository-url>
cd mas-665-hw2

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
source .venv/bin/activate
```

This will automatically:
- Create a virtual environment with Python 3.11.11
- Install all project dependencies
- Set up the development environment

### Dependency Management

This project uses `uv` for fast dependency management. The project includes both:
- **`pyproject.toml`**: Primary dependency specification (managed by `uv`)
- **`requirements.txt`**: Generated dependency file for compatibility

**Adding new dependencies:**
```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update requirements.txt after adding dependencies
uv pip freeze > requirements.txt
```

**Note**: Always run `uv pip freeze > requirements.txt` after adding new dependencies via `uv` to keep the requirements.txt file synchronized with your current environment.

### 3. Development Setup (Pre-commit Hooks)

This project uses pre-commit hooks to ensure code quality and consistency. After cloning and setting up the project, install the pre-commit hooks:

```bash
# Install pre-commit hooks
uv run pre-commit install
```

### 4. Configuration

### 5. Running the Sarcastic Agent

The project uses `pyproject.toml` to define convenient scripts. To start the sarcastic agent server, run:

```bash
uv run start-local
```

This will launch the Nanda adapter server with the sarcastic agent running on port 6000.

## API Endpoints Testing

The sarcastic agent server provides both agent bridge and Flask API endpoints. All endpoints are always available regardless of environment configuration.

### Available Endpoints

```bash
# Health check
curl http://localhost:6001/api/health

# Send message to agent (main endpoint for testing)
curl -X POST http://localhost:6001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world", "conversation_id": "test-123", "client_id": "test-client"}'

# List registered agents
curl http://localhost:6001/api/agents/list

# Get latest message
curl http://localhost:6001/api/render

# Stream messages (Server-Sent Events)
curl http://localhost:6001/api/messages/stream?client_id=test-client

# Agent bridge connectivity (A2A protocol)
curl http://localhost:6000/a2a
```

### Testing the Sarcastic Transformation
The `/api/send` endpoint is the primary way to test the sarcastic agent:

```bash
# Basic message test
curl -X POST http://localhost:6001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "This is a great day!"}'

# With conversation tracking
curl -X POST http://localhost:6001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "I love this weather", "conversation_id": "weather-chat", "client_id": "user-123"}'
```

**Note**: The server runs both the agent bridge (port 6000) and Flask API (port 6001). Environment variables control SSL, domain, and other configuration options.

## Project Structure

## Assignment Documentation

## 🤖 AI Development Tools Used

### **Cursor AI Assistant**
This project was developed entirely using Cursor. **All code, including this README, was written via prompting Cursor for changes.**

### **Implementation Approach**

## 🔮 Future Extensions

### **Playwright MCP Integration**
The repository includes a `playwright-mcp` submodule for future iterations that will add MCP (Model Context Protocol) as a tool, enabling web automation capabilities for the agents.

### **Multi-Crew Architecture**
The custom chat implementation is designed to be extended, allowing agents to access multiple crews as tools rather than being limited to a single crew. This will enable more sophisticated workflows and specialized task delegation.
