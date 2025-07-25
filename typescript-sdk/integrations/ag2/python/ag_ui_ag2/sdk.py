"""
SDK for AG2 integration with AG-UI
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


class AG2Flow:
    """
    AG2 Flow integration with AG-UI protocol
    """
    
    def __init__(self, agents: List[Any], state: Optional[CopilotKitState] = None):
        self.agents = agents
        self.state = state or CopilotKitState()
        self.encoder = EventEncoder()
        
    async def emit_event(self, event):
        """Emit an event (for demo purposes, just print)"""
        encoded = self.encoder.encode(event)
        print(encoded.strip())  # Remove trailing newlines for cleaner output
        
    async def start_conversation(self):
        """Start the multi-agent conversation"""
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
            
            # Start the multi-agent conversation
            conversation_history = []
            
            for i, agent in enumerate(self.agents):
                # Emit step started for current agent
                agent_name = getattr(agent, 'name', f'Agent_{i}')
                await self._emit_step_started(f"agent_{i}_thinking")
                
                if i == 0:
                    # First agent responds to user message
                    prompt = f"User said: {last_user_message}. Please provide a helpful response."
                else:
                    # Subsequent agents respond to previous agents
                    prev_response = conversation_history[-1] if conversation_history else ""
                    prompt = f"Previous agent said: {prev_response}. Please provide your perspective or build upon this."
                
                # Get agent response (this would be replaced with actual AG2 agent.generate_response())
                response = await self._get_agent_response(agent, prompt)
                conversation_history.append(response)
                
                # Emit the agent's response
                await self._emit_message(f"**{agent_name}**: {response}")
                
                # Emit step finished
                await self._emit_step_finished(f"agent_{i}_thinking")
                
                # Small delay between agents
                await asyncio.sleep(0.5)
                
            # Final summary
            await self._emit_run_finished(run_id)
            
        except Exception as e:
            await self._emit_message(f"Error in conversation: {str(e)}")
            await self._emit_run_finished(run_id)
    
    async def _get_agent_response(self, agent, prompt: str) -> str:
        """Get response from AG2 agent (simplified for demo)"""
        # This is a simplified version - in real implementation, 
        # you would use AG2's actual agent.generate_response() method
        agent_name = getattr(agent, 'name', 'Agent')
        system_message = getattr(agent, 'system_message', 'You are a helpful assistant')
        
        # For demo purposes, create a simple response based on agent's role
        if 'critic' in agent_name.lower():
            return f"As a critic, I think we should consider the potential drawbacks and alternatives to this approach."
        elif 'assistant' in agent_name.lower():
            return f"I understand your request. Let me provide a helpful response based on my role as an assistant."
        else:
            return f"From my perspective as {agent_name}, I think this is an interesting point that deserves careful consideration."
    
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


async def copilotkit_stream(ag2_response):
    """
    Stream AG2 responses to CopilotKit format
    """
    # This function would adapt AG2's streaming response format
    # to AG-UI's expected format
    return ag2_response