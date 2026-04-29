"""Unit tests for the A2A agent client module."""
import pytest # pyright: ignore[reportMissingImports]
from unittest.mock import patch, AsyncMock, MagicMock
from src.client import process_response, main # pyright: ignore[reportMissingImports]


def test_process_response_with_error():
    """Test that process_response handles error responses correctly."""
    result = {
        "error": {"code": -32600, "message": "Invalid Request"}
    }
    
    with patch('builtins.print') as mock_print:
        process_response(result)
        mock_print.assert_called_once_with("Error:", {"code": -32600, "message": "Invalid Request"})


def test_process_response_with_no_result():
    """Test that process_response handles responses with no result."""
    result = {"jsonrpc": "2.0", "id": "1"}
    
    with patch('builtins.print') as mock_print:
        process_response(result)
        mock_print.assert_not_called()


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


def test_process_response_with_task_message():
    """Test that process_response handles task status messages."""
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
    
    with patch('builtins.print') as mock_print:
        process_response(result)
        mock_print.assert_called_with("Agent says: Task completed")


def test_process_response_with_multiple_parts():
    """Test that process_response handles messages with multiple parts."""
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
    
    with patch('builtins.print') as mock_print:
        process_response(result)
        assert mock_print.call_count == 2
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert "Agent says: First part" in calls
        assert "Agent says: Second part" in calls
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

    with patch('httpx.AsyncClient') as mock_client_class:
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
            
            assert mock_print.call_count >= 1
