"""A2A Agent Client implementation.

This module provides a client to connect to an A2A agent server,
fetch its agent card, and send messages.

Example:
    Run the client with:
    >>> python -m src.client
"""
import asyncio
import os
import httpx  # pyright: ignore[reportMissingImports]
import uuid
import aioconsole  # pyright: ignore[reportMissingImports]

AGENT_URL = os.getenv("A2A_AGENT_URL", "http://localhost:8080")
JSONRPC_ID = "1"


def extract_response_texts(result: dict) -> list[str]:
    """Extract text parts from a JSON-RPC response.

    Args:
        result: The JSON-RPC response dictionary from the agent server.

    Returns:
        List of text strings extracted from the response.
    """
    texts = []

    if "error" in result:
        texts.append(f"Error: {result['error']}")
        return texts

    res = result.get("result")
    if not res:
        return texts

    msg = None
    if "message" in res:
        msg = res["message"]
        
    elif "task" in res:
        msg = res.get("task", {}).get("status", {}).get("message")

    if not msg or "parts" not in msg:
        return texts

    for part in msg["parts"]:
        if "text" in part:
            texts.append(part["text"])

    return texts


def process_response(result: dict) -> None:
    """Process and print the agent's response from the JSON-RPC result.

    Args:
        result: The JSON-RPC response dictionary from the agent server.
    """
    for text in extract_response_texts(result):
        print(f"Agent says: {text}")


async def main():
    """Main async function to connect to the agent and send a message.

    Fetches the agent card, sends a greeting message, and prints the response.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AGENT_URL}/.well-known/agent-card.json")
            response.raise_for_status()
            agent_card = response.json()
            print(f"Connected to agent: {agent_card['name']}")
        except httpx.HTTPError as e:
            print(f"Error fetching agent card: {e}")
            return

        user_message = await aioconsole.ainput("Enter your message to the agent: ")

        request = {
            "jsonrpc": "2.0",
            "id": JSONRPC_ID,
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "ROLE_USER",
                    "parts": [{"text": user_message}],
                }
            },
        }

        try:
            response = await client.post(
                AGENT_URL + "/",
                json=request,
                headers={"Content-Type": "application/json", "A2A-Version": "1.0"},
            )
            print("Status:", response.status_code)
            response.raise_for_status()
            process_response(response.json())
        except httpx.HTTPError as e:
            print(f"Error communicating with agent: {e}")


if __name__ == "__main__":
    asyncio.run(main())