"""A2A Agent Client implementation.

This module provides a client to connect to an A2A agent server,
fetch its agent card, and send messages.

Example:
    Run the client with:
    >>> python -m src.client
"""
import asyncio
import httpx  # pyright: ignore[reportMissingImports]
import uuid


def process_response(result: dict):
    """Process and print the agent's response from the JSON-RPC result.
    
    Args:
        result: The JSON-RPC response dictionary from the agent server.
    """
    if "error" in result:
        print("Error:", result["error"])
        return

    res = result.get("result")
    if not res:
        return

    msg = res.get("message") or res.get("task", {}).get("status", {}).get("message")
    if not msg or "parts" not in msg:
        return

    for part in msg["parts"]:
        if "text" in part:
            print(f"Agent says: {part['text']}")


async def main():
    """Main async function to connect to the agent and send a message.
    
    Fetches the agent card, sends a greeting message, and prints the response.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/.well-known/agent-card.json")
        agent_card = response.json()
        print(f"Connected to agent: {agent_card['name']}")

        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "ROLE_USER",
                    "parts": [{"text": "Hello! Can you help me?"}],
                }
            },
        }

        response = await client.post(
            "http://localhost:8080/",
            json=request,
            headers={"Content-Type": "application/json", "A2A-Version": "1.0"},
        )
        print("Status:", response.status_code)
        process_response(response.json())


if __name__ == "__main__":
    asyncio.run(main())