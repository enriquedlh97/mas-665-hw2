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

### 5. Running the Chat
The project uses `pyproject.toml` to define convenient scripts. To start the chat interface, run:

```bash
chat
```

or if for some reason that files, run
```
uv run chat
```

This will launch the interactive terminal where you can converse with the agent.

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
