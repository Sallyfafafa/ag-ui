"""
Minimal AG2 Multi-Agent Chat Example

This example demonstrates a simple multi-agent conversation using AG2 and AG-UI.
Two agents (an assistant and a critic) will discuss a user's input.
"""

import asyncio
import os
import sys
from typing import List

# Add the parent directory to the path so we can import ag_ui_ag2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ag_ui_ag2 import AG2Flow, CopilotKitState


class MockAG2Agent:
    """Mock AG2 Agent for demonstration purposes"""
    
    def __init__(self, name: str, system_message: str):
        self.name = name
        self.system_message = system_message
    
    async def generate_response(self, prompt: str) -> str:
        """Simulate AG2 agent response generation"""
        # In a real implementation, this would call AG2's LLM
        if "assistant" in self.name.lower():
            return f"As your assistant, I think {prompt.lower()} is an interesting topic. Let me help you explore this further."
        elif "critic" in self.name.lower():
            return f"As a critic, I should point out some potential issues with this approach. Have you considered the alternatives?"
        else:
            return f"From my perspective as {self.name}, this requires careful consideration."


async def run_ag2_chat_example():
    """Run the AG2 chat example"""
    
    # Create AG2 agents
    agents = [
        MockAG2Agent(
            name="helpful_assistant",
            system_message="You are a helpful assistant that provides constructive advice."
        ),
        MockAG2Agent(
            name="critical_reviewer", 
            system_message="You are a critical reviewer that points out potential issues and improvements."
        )
    ]
    
    # Create CopilotKit state with a sample user message
    state = CopilotKitState()
    state.messages = [
        {
            "role": "user",
            "content": "I want to build a web application using Python. What should I consider?"
        }
    ]
    
    # Create and run the AG2 flow
    print("🤖 Starting AG2 Multi-Agent Conversation...")
    print("=" * 50)
    
    flow = AG2Flow(agents=agents, state=state)
    await flow.start_conversation()
    
    print("=" * 50)
    print("✅ Conversation completed!")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found. Using mock responses.")
        print("   For real AG2 integration, set your OpenAI API key.")
        print("")
    
    # Run the example
    asyncio.run(run_ag2_chat_example())