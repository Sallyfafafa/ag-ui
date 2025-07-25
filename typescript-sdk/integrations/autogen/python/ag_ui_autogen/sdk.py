"""
SDK for AutoGen integration with AG-UI
"""

import asyncio
import uuid
from typing import List, Any, Dict, Optional
from ag_ui.core.events import (
    TextMessageStartEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    RunStartedEvent,
    RunFinishedEvent,
    StepStartedEvent,
    StepFinishedEvent,
)
from ag_ui.core.types import (
    AssistantMessage,
)
from ag_ui.encoder.encoder import EventEncoder


class CopilotKitState:
    """State object that holds CopilotKit context and messages"""
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.copilotkit = None
        self.state: Dict[str, Any] = {}


class AutoGenFlow:
    """
    AutoGen Flow integration with AG-UI protocol
    """
    
    def __init__(self, agents: List[Any], state: Optional[CopilotKitState] = None):
        self.agents = agents
        self.state = state or CopilotKitState()
        self.encoder = EventEncoder()
        
    async def emit_event(self, event):
        """Emit an event (for demo purposes, just print)"""
        encoded = self.encoder.encode(event)
        print(encoded.strip())  # Remove trailing newlines for cleaner output
        
    async def start_group_chat(self):
        """Start the AutoGen group chat"""
        try:
            run_id = str(uuid.uuid4())
            
            # Emit run started event
            await self._emit_run_started(run_id)
            
            # Get the last user message
            user_messages = [msg for msg in self.state.messages if msg.get("role") == "user"]
            if not user_messages:
                await self._emit_message("Please provide a message to start the conversation.")
                await self._emit_run_finished(run_id)
                return
                
            last_user_message = user_messages[-1]["content"]
            
            # Simulate AutoGen group chat
            await self._emit_step_started("initializing_agents")
            
            # For demo purposes, simulate a conversation between agents
            conversation_turns = 3  # Number of turns in the conversation
            
            for turn in range(conversation_turns):
                for i, agent in enumerate(self.agents):
                    agent_name = getattr(agent, 'name', f'Agent_{i}')
                    
                    # Emit step started for current agent
                    await self._emit_step_started(f"agent_turn_{agent_name}_turn_{turn+1}")
                    
                    # Get agent response
                    if turn == 0 and i == 0:
                        # First agent responds to user
                        prompt = last_user_message
                    else:
                        # Subsequent responses build on the conversation
                        prompt = "Please continue the conversation based on the previous discussion."
                    
                    response = await self._get_agent_response(agent, prompt, turn)
                    
                    # Emit the agent's response
                    await self._emit_message(f"**{agent_name}** (Turn {turn + 1}): {response}")
                    
                    # Emit step finished
                    await self._emit_step_finished(f"agent_turn_{agent_name}_turn_{turn+1}")
                    
                    # Small delay between agents
                    await asyncio.sleep(0.3)
                    
                # Delay between conversation turns
                if turn < conversation_turns - 1:
                    await asyncio.sleep(0.5)
                    
            # Final summary
            await self._emit_step_finished("initializing_agents")
            await self._emit_message("🎯 **Summary**: The agents have completed their discussion. Each agent provided their perspective on your question.")
            await self._emit_run_finished(run_id)
            
        except Exception as e:
            await self._emit_message(f"Error in group chat: {str(e)}")
            await self._emit_run_finished(run_id)
    
    async def _get_agent_response(self, agent, prompt: str, turn: int) -> str:
        """Get response from AutoGen agent (simplified for demo)"""
        # This is a simplified version - in real implementation, 
        # you would use AutoGen's actual agent response methods
        agent_name = getattr(agent, 'name', 'Agent')
        
        # Create different responses based on agent type and turn
        if 'user_proxy' in agent_name.lower() or 'user' in agent_name.lower():
            if turn == 0:
                return f"I'll help coordinate this discussion. Let me pass this to our assistant for analysis."
            else:
                return f"Based on the assistant's input, I think we should also consider the practical implementation aspects."
        elif 'assistant' in agent_name.lower():
            responses = [
                f"I understand your question. Let me break this down systematically.",
                f"Building on the previous discussion, here are some additional considerations.",
                f"To conclude, I believe we've covered the main aspects of your question."
            ]
            return responses[min(turn, len(responses) - 1)]
        else:
            return f"From the perspective of {agent_name}, this is an interesting challenge that requires careful analysis."
    
    async def _emit_message(self, content: str):
        """Emit a message event"""
        message_id = str(uuid.uuid4())
        
        # Start message
        start_event = TextMessageStartEvent(
            message_id=message_id,
            role="assistant"
        )
        await self.emit_event(start_event)
        
        # Message content
        content_event = TextMessageContentEvent(
            message_id=message_id,
            delta=content
        )
        await self.emit_event(content_event)
        
        # End message
        end_event = TextMessageEndEvent(
            message_id=message_id
        )
        await self.emit_event(end_event)
    
    async def _emit_run_started(self, run_id: str):
        """Emit run started event"""
        event = RunStartedEvent(
            thread_id="default",
            run_id=run_id
        )
        await self.emit_event(event)
    
    async def _emit_run_finished(self, run_id: str):
        """Emit run finished event"""
        event = RunFinishedEvent(
            thread_id="default",
            run_id=run_id
        )
        await self.emit_event(event)
    
    async def _emit_step_started(self, step_name: str):
        """Emit step started event"""
        event = StepStartedEvent(
            step_name=step_name
        )
        await self.emit_event(event)
    
    async def _emit_step_finished(self, step_name: str):
        """Emit step finished event"""
        event = StepFinishedEvent(
            step_name=step_name
        )
        await self.emit_event(event)


async def copilotkit_stream(autogen_response):
    """
    Stream AutoGen responses to CopilotKit format
    """
    # This function would adapt AutoGen's streaming response format
    # to AG-UI's expected format
    return autogen_response