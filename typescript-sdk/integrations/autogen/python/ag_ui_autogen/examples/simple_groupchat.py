"""
Simple AutoGen Group Chat Example

This example demonstrates a basic AutoGen group chat using AG-UI.
Multiple agents will participate in a structured conversation.
"""

import asyncio
import os
import sys
from typing import List

# Add the parent directory to the path so we can import ag_ui_autogen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ag_ui_autogen import AutoGenFlow, CopilotKitState


class MockAutoGenAgent:
    """Mock AutoGen Agent for demonstration purposes"""
    
    def __init__(self, name: str, human_input_mode: str = "NEVER", max_consecutive_auto_reply: int = 10):
        self.name = name
        self.human_input_mode = human_input_mode
        self.max_consecutive_auto_reply = max_consecutive_auto_reply
    
    async def generate_reply(self, messages: List[dict]) -> str:
        """Simulate AutoGen agent reply generation"""
        # In a real implementation, this would call AutoGen's LLM
        if "user_proxy" in self.name.lower():
            return f"As the user proxy, I'll coordinate this discussion and ensure we address your needs."
        elif "assistant" in self.name.lower():
            return f"As an assistant, I'm here to provide detailed analysis and helpful solutions."
        elif "critic" in self.name.lower():
            return f"As a critic, I'll examine potential issues and suggest improvements."
        else:
            return f"From the perspective of {self.name}, let me share my insights on this topic."


async def run_autogen_groupchat_example():
    """Run the AutoGen group chat example"""
    
    # Create AutoGen agents
    agents = [
        MockAutoGenAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3
        ),
        MockAutoGenAgent(
            name="helpful_assistant",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3
        ),
        MockAutoGenAgent(
            name="critical_analyst",
            human_input_mode="NEVER", 
            max_consecutive_auto_reply=3
        )
    ]
    
    # Create CopilotKit state with a sample user message
    state = CopilotKitState()
    state.messages = [
        {
            "role": "user",
            "content": "I need help designing a scalable microservices architecture. What are the key considerations?"
        }
    ]
    
    # Create and run the AutoGen flow
    print("🤖 Starting AutoGen Group Chat...")
    print("=" * 50)
    
    flow = AutoGenFlow(agents=agents, state=state)
    await flow.start_group_chat()
    
    print("=" * 50)
    print("✅ Group chat completed!")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found. Using mock responses.")
        print("   For real AutoGen integration, set your OpenAI API key.")
        print("")
    
    # Run the example
    asyncio.run(run_autogen_groupchat_example())