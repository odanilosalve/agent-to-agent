# A2A Test Project

This project is a minimal implementation of the Agent-to-Agent (A2A) communication protocol, featuring a simple "Hello Agent" server and a corresponding client.

## Project Structure

- `src/server.py`: The agent server implementation using Starlette and Uvicorn.
- `src/client.py`: The client implementation to interact with the agent.
- `tests/`: Unit tests for the project.

## Prerequisites

- Python 3.14.4 (as specified in `.python-version`)
- Virtual environment (recommended)

## Setup

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *Note: Ensure you have access to the `a2a` internal library if it's not hosted on a public repository.*

## Running the Project

### 1. Start the Server

The server hosts the "Hello Agent" and listens for requests on `127.0.0.1:8080`.

```bash
python -m src.server
```

### 2. Run the Client

In a separate terminal, run the client to connect to the server, fetch the agent card, and send a message.

```bash
python -m src.client
```

## Running Tests

To run the unit tests, use `pytest`:

```bash
pytest
```

## Protocol Details

- **Discovery:** The server exposes an agent card at `http://127.0.0.1:8080/.well-known/agent-card.json`.
- **Communication:** Uses JSON-RPC 2.0 over HTTP.
- **A2A Version:** Currently implements and expects version `1.0`.
