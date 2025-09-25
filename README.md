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

curl -X POST https://citana.io:6001/api/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello world", "conversation_id": "test-123", "client_id": "test-client"}'

# Forces agent call when registry fails and bridge defaults to generic call
curl -X POST https://citana.io:6001/api/send \
-H "Content-Type: application/json" \
-d '{"message": "@local Hello, hows it going? and what is your name?", "conversation_id": "test-123", "client_id": "test-client"}'

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

## Production Deployment on EC2 (Amazon Linux)

### 1) One-time EC2 Setup

```bash
# Update base system and install required tools
sudo dnf update -y
sudo dnf install -y git make python3.11 python3.11-pip certbot

# Install uv (adds to ~/.local/bin)
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Clone and prepare repo
cd ~
git clone <repository-url>
cd mas-665-hw2
git checkout feat/example-setup

# Install project dependencies from pyproject.toml
uv sync
```

Networking prerequisites:
- Open your EC2 Security Group ingress for TCP 80 (for cert issuance) and TCP 6001 (agent HTTPS).
- Ensure nothing is listening on port 80 before issuing certs:

```bash
sudo ss -ltnp | awk 'NR==1 || /:80 /'
```

### 2) Generate SSL Certificates (Let’s Encrypt)

```bash
# Issue cert for your domain (DNS A record must point to this EC2's public IP)
sudo certbot certonly --standalone -d citana.io

# Copy certs to the repo run directory (used by the adapter)
cd ~/mas-665-hw2
sudo cp -L /etc/letsencrypt/live/citana.io/fullchain.pem .
sudo cp -L /etc/letsencrypt/live/citana.io/privkey.pem .
sudo chown $USER:$USER fullchain.pem privkey.pem
chmod 600 fullchain.pem privkey.pem
```

### 3) Configure Environment

Create or update `.env` in the repo root:

```
DOMAIN_NAME=citana.io
ssl_enabled=true
agent_port=6000
PUBLIC_URL=https://citana.io:6001
ANTHROPIC_API_KEY=YOUR_KEY
```

### 4) Run the Agent

We provide a Make target that ensures environment variables from `.env` (including `ANTHROPIC_API_KEY`) are loaded correctly via `uv --env-file .env` before starting the server.

Foreground (recommended for validation):

```bash
cd ~/mas-665-hw2
make start-local
```

Preferred workflow: keep the agent running in this foreground terminal to see live logs, and open a second terminal for running curl tests and other commands. This avoids backgrounding and makes debugging simpler.

Background (optional):

```bash
cd ~/mas-665-hw2
nohup make start-local > out.log 2>&1 &
tail -f out.log
```

Health check:

```bash
curl -sfk https://citana.io:6001/api/health | cat
```

Enrollment (from logs):

```bash
grep -i "enroll" out.log | tail -n 5 | cat
# Open the printed enrollment link in a browser and complete registration
```

### 5) Certificate Renewal and Reboots

- Certbot auto-renews certificates under `/etc/letsencrypt/live/citana.io/` via a system timer.
- If you copied certs into the repo directory, they will NOT update automatically on renewal.
  - Option A (re-copy after renewal):

```bash
sudo cp -L /etc/letsencrypt/live/citana.io/fullchain.pem ~/mas-665-hw2/
sudo cp -L /etc/letsencrypt/live/citana.io/privkey.pem ~/mas-665-hw2/
```

  - Option B (preferred: symlink so renewals take effect automatically):

```bash
cd ~/mas-665-hw2
ln -sf /etc/letsencrypt/live/citana.io/fullchain.pem fullchain.pem
ln -sf /etc/letsencrypt/live/citana.io/privkey.pem privkey.pem
sudo chown -h $USER:$USER fullchain.pem privkey.pem
```

- Reboots: you do not need to reissue certificates. Start the agent again:

```bash
cd ~/mas-665-hw2
uv run start-local
```

- Instance termination / new EC2 instance:
  - Certificates and private keys are stored on-disk under `/etc/letsencrypt/`. If you terminate the instance and create a new one, those files are gone unless you restore from an AMI/snapshot.
  - For a fresh instance, re-run the setup: install certbot, ensure DNS A record points to the new public IP, and issue a new cert with `sudo certbot certonly --standalone -d citana.io`, then copy/symlink the certs into the repo directory as above.
  - If you created the new instance from an AMI that already contains `/etc/letsencrypt/`, you do not need to reissue; certbot will continue to renew on schedule. Just ensure DNS points to the new IP and start the agent.

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
