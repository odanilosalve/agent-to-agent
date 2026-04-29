import os

# Server Configuration
SERVER_HOST = os.getenv("A2A_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("A2A_SERVER_PORT", "8080"))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

# Agent Card Configuration
AGENT_NAME = "Hello Agent"
AGENT_VERSION = "1.0.0"
AGENT_DESCRIPTION = "A simple agent that says hello"

# API Configuration
JSONRPC_VERSION = "2.0"
A2A_VERSION = "1.0"
