"""Unit tests for the A2A agent client module."""
import pytest  # pyright: ignore[reportMissingImports]
from unittest.mock import patch, AsyncMock, MagicMock
from src.client import extract_response_texts, process_response, main  # pyright: ignore[reportMissingImports]


def test_extract_response_texts_with_error():
    """Test that extract_response_texts handles error responses correctly."""
    result = {
        "error": {"code": -32600, "message": "Invalid Request"}
    }

    texts = extract_response_texts(result)
    assert len(texts) == 1
    assert "Error:" in texts[0]


def test_extract_response_texts_with_no_result():
    """Test that extract_response_texts handles responses with no result."""
    result = {"jsonrpc": "2.0", "id": "1"}

    texts = extract_response_texts(result)
    assert texts == []


def test_extract_response_texts_with_message():
    """Test that extract_response_texts correctly extracts agent responses."""
    result = {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "message": {
                "parts": [{"text": "Hello! You said: Hi there"}]
            }
        }
    }

    texts = extract_response_texts(result)
    assert texts == ["Hello! You said: Hi there"]


def test_extract_response_texts_with_task_message():
    """Test that extract_response_texts handles task status messages."""
    result = {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "task": {
                "status": {
                    "message": {
                        "parts": [{"text": "Task completed"}]
                    }
                }
            }
        }
    }

    texts = extract_response_texts(result)
    assert texts == ["Task completed"]


def test_extract_response_texts_with_multiple_parts():
    """Test that extract_response_texts handles messages with multiple parts."""
    result = {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "message": {
                "parts": [
                    {"text": "First part"},
                    {"text": "Second part"}
                ]
            }
        }
    }

    texts = extract_response_texts(result)
    assert texts == ["First part", "Second part"]


def test_process_response_with_error():
    """Test that process_response handles error responses correctly."""
    result = {
        "error": {"code": -32600, "message": "Invalid Request"}
    }

    with patch('builtins.print') as mock_print:
        process_response(result)
        mock_print.assert_called_once()
        assert "Error:" in mock_print.call_args[0][0]


def test_process_response_with_message():
    """Test that process_response correctly prints agent responses."""
    result = {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "message": {
                "parts": [{"text": "Hello! You said: Hi there"}]
            }
        }
    }

    with patch('builtins.print') as mock_print:
        process_response(result)
        mock_print.assert_called_with("Agent says: Hello! You said: Hi there")


@pytest.mark.asyncio
async def test_main_function():
    """Test the main client function."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": "1",
        "result": {
            "message": {
                "parts": [{"text": "Hello! You said: Hello! Can you help me?"}]
            }
        }
    }

    mock_agent_card_response = MagicMock()
    mock_agent_card_response.json.return_value = {"name": "Hello Agent"}

    with patch('httpx.AsyncClient') as mock_client_class, \
         patch('src.client.aioconsole.ainput', return_value="Hello! Can you help me?") as mock_ainput:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup responses
        mock_client.get.return_value = mock_agent_card_response
        mock_client.post.return_value = mock_response

        with patch('builtins.print') as mock_print:
            await main()

            mock_client.get.assert_called_once()
            mock_client.post.assert_called_once()
            mock_ainput.assert_called_once()

            assert mock_print.call_count >= 1
