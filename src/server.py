"""A2A Agent Server implementation.

This module provides a simple A2A (Agent-to-Agent) server that responds
to user messages with a greeting.

Example:
    Run the server with:
    >>> python -m src.server
    
    Or import and use programmatically:
    >>> from src.server import agent_card, handler
"""
import uuid
import uvicorn # pyright: ignore[reportMissingImports]
from starlette.applications import Starlette # type: ignore
from a2a.server.request_handlers import DefaultRequestHandlerV2 # type: ignore
from a2a.server.routes import ( # pyright: ignore[reportMissingImports]
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore # pyright: ignore[reportMissingImports]
from a2a.server.agent_execution import AgentExecutor, RequestContext # pyright: ignore[reportMissingImports]
from a2a.server.events import EventQueue # pyright: ignore[reportMissingImports]
from a2a.types import ( # pyright: ignore[reportMissingImports]
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    AgentInterface,
    Message,
    Part,
    TaskStatus,
    TaskState,
    TaskStatusUpdateEvent,
    Role,
    Task,
)


class HelloAgentExecutor(AgentExecutor):
    """Executor that handles incoming requests and generates responses for the Hello Agent."""

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute the agent's main logic to process user messages.
        
        Args:
            context: The request context containing the incoming message.
            event_queue: Queue for sending events back to the client.
        """
        user_message = context.message
        if user_message and user_message.parts:
            user_text = user_message.parts[0].text
            await event_queue.enqueue_event(
                Task(
                    id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(state=TaskState.TASK_STATE_WORKING),
                )
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(
                        state=TaskState.TASK_STATE_WORKING,
                    ),
                )
            )
            
            response_text = f"Hello! You said: {user_text}"
            response_message = Message(
                message_id=str(uuid.uuid4()),
                role=Role.ROLE_AGENT,
                parts=[Part(text=response_text)],
            )
            await event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    task_id=context.task_id,
                    context_id=context.context_id,
                    status=TaskStatus(
                        state=TaskState.TASK_STATE_COMPLETED,
                        message=response_message,
                    ),
                )
            )

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel any ongoing agent execution.
        
        This agent completes tasks immediately, so there's nothing to cancel.
        
        Args:
            context: The request context.
            event_queue: Queue for sending events back to the client.
        """
        # HelloAgentExecutor completes tasks immediately; no background processing to cancel.
        pass


agent_card = AgentCard(
    name="Hello Agent",
    description="A simple agent that says hello",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(
            url="http://localhost:8080",
            protocol_binding="agent-card",
            protocol_version="1.0",
        )
    ],
    skills=[AgentSkill(id="greet", name="Greet", description="Greets the user")],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
)

handler = DefaultRequestHandlerV2(
    agent_executor=HelloAgentExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

routes = (
    create_agent_card_routes(agent_card)
    + create_jsonrpc_routes(handler, "/", enable_v0_3_compat=True)
)

app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)