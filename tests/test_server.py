"""Unit tests for the A2A agent server module."""
import pytest # pyright: ignore[reportMissingImports]
import uuid
from unittest.mock import AsyncMock, MagicMock
from src.server import HelloAgentExecutor, agent_card # type: ignore
from a2a.server.agent_execution import RequestContext # pyright: ignore[reportMissingImports]
from a2a.types import Message, Part, Role, TaskStatus, TaskState # pyright: ignore[reportMissingImports]


@pytest.mark.asyncio
async def test_hello_agent_executor_execute():
    """Test that HelloAgentExecutor correctly processes user messages."""
    executor = HelloAgentExecutor()
    
    event_queue = AsyncMock()
    context = MagicMock(spec=RequestContext)
    context.task_id = str(uuid.uuid4())
    context.context_id = str(uuid.uuid4())
    context.message = Message(
        message_id=str(uuid.uuid4()),
        role=Role.ROLE_USER,
        parts=[Part(text="Hello there!")]
    )
    
    await executor.execute(context, event_queue)

    assert event_queue.enqueue_event.called
    assert event_queue.enqueue_event.call_count >= 3


@pytest.mark.asyncio
async def test_hello_agent_executor_cancel():
    """Test that HelloAgentExecutor's cancel method completes without error."""
    executor = HelloAgentExecutor()
    
    event_queue = AsyncMock()
    context = MagicMock(spec=RequestContext)
    
    await executor.cancel(context, event_queue)


def test_agent_card_configuration():
    """Test that the agent card is properly configured."""
    assert agent_card.name == "Hello Agent"
    assert agent_card.description == "A simple agent that says hello"
    assert agent_card.version == "1.0.0"
    assert len(agent_card.skills) == 1
    assert agent_card.skills[0].id == "greet"
    assert agent_card.skills[0].name == "Greet"


def test_agent_card_interface():
    """Test that the agent card has proper interface configuration."""
    assert len(agent_card.supported_interfaces) == 1
    interface = agent_card.supported_interfaces[0]
    assert interface.url == "http://localhost:8080"
    assert interface.protocol_binding == "agent-card"
    assert interface.protocol_version == "1.0"


def test_agent_card_modes():
    """Test that the agent card has proper input/output modes."""
    assert "text/plain" in agent_card.default_input_modes
    assert "text/plain" in agent_card.default_output_modes
