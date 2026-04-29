"""Unit tests for the A2A agent server module."""
import pytest  # pyright: ignore[reportMissingImports]
import uuid
from unittest.mock import AsyncMock, MagicMock
from src.server import HelloAgentExecutor, create_agent_card, create_app  # type: ignore
from src import config
from a2a.server.agent_execution import RequestContext  # pyright: ignore[reportMissingImports]
from a2a.types import Message, Part, Role, Task, TaskStatus, TaskState, TaskStatusUpdateEvent  # pyright: ignore[reportMissingImports]


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
    assert event_queue.enqueue_event.call_count == 2

    # Verify the events: Task first, then TaskStatusUpdateEvent
    calls = event_queue.enqueue_event.call_args_list
    assert isinstance(calls[0][0][0], Task)
    assert isinstance(calls[1][0][0], TaskStatusUpdateEvent)
    assert calls[0][0][0].status.state == TaskState.TASK_STATE_WORKING
    assert calls[1][0][0].status.state == TaskState.TASK_STATE_COMPLETED


@pytest.mark.asyncio
async def test_hello_agent_executor_execute_no_message():
    """Test that HelloAgentExecutor handles missing message gracefully."""
    executor = HelloAgentExecutor()

    event_queue = AsyncMock()
    context = MagicMock(spec=RequestContext)
    context.message = None

    await executor.execute(context, event_queue)

    event_queue.enqueue_event.assert_not_called()


@pytest.mark.asyncio
async def test_hello_agent_executor_execute_empty_parts():
    """Test that HelloAgentExecutor handles empty parts gracefully."""
    executor = HelloAgentExecutor()

    event_queue = AsyncMock()
    context = MagicMock(spec=RequestContext)
    context.message = Message(
        message_id=str(uuid.uuid4()),
        role=Role.ROLE_USER,
        parts=[]
    )

    await executor.execute(context, event_queue)

    event_queue.enqueue_event.assert_not_called()


@pytest.mark.asyncio
async def test_hello_agent_executor_cancel():
    """Test that HelloAgentExecutor's cancel method completes without error."""
    executor = HelloAgentExecutor()

    event_queue = AsyncMock()
    context = MagicMock(spec=RequestContext)

    # Should not raise any exception
    await executor.cancel(context, event_queue)

    # Should not enqueue any events
    event_queue.enqueue_event.assert_not_called()


def test_create_agent_card():
    """Test that create_agent_card returns a properly configured AgentCard."""
    agent_card = create_agent_card()
    assert agent_card.name == config.AGENT_NAME
    assert agent_card.description == config.AGENT_DESCRIPTION
    assert agent_card.version == config.AGENT_VERSION
    assert len(agent_card.skills) == 1
    assert agent_card.skills[0].id == "greet"
    assert agent_card.skills[0].name == "Greet"


def test_create_agent_card_interface():
    """Test that the agent card has proper interface configuration."""
    agent_card = create_agent_card()
    assert len(agent_card.supported_interfaces) == 1
    interface = agent_card.supported_interfaces[0]
    assert interface.url == config.SERVER_URL
    assert interface.protocol_binding == "agent-card"
    assert interface.protocol_version == config.A2A_VERSION


def test_create_agent_card_modes():
    """Test that the agent card has proper input/output modes."""
    agent_card = create_agent_card()
    assert "text/plain" in agent_card.default_input_modes
    assert "text/plain" in agent_card.default_output_modes


def test_create_app():
    """Test that create_app returns a Starlette application."""
    app = create_app()
    assert app is not None
