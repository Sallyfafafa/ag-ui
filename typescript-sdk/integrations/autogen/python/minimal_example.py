#!/usr/bin/env python3
"""
最小的 AutoGen 集成示例

这个示例展示了如何使用 AG-UI 与 AutoGen 集成的最简单方法。
运行这个脚本，你将看到 AutoGen 群聊的效果。
"""

import asyncio
import os
import sys
import uuid

# 添加项目路径到 Python 路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
# 添加 ag-ui 核心库路径
ag_ui_root = os.path.join(os.path.dirname(project_root), '..', '..', '..', 'python-sdk')
sys.path.insert(0, ag_ui_root)

try:
    from ag_ui.core.events import (
        TextMessageStartEvent,
        TextMessageContentEvent, 
        TextMessageEndEvent,
        RunStartedEvent,
        RunFinishedEvent,
        StepStartedEvent,
        StepFinishedEvent,
    )
    from ag_ui.encoder.encoder import EventEncoder
except ImportError as e:
    print(f"❌ 无法导入 ag-ui 库: {e}")
    print("请确保已安装 ag-ui-protocol 包")
    sys.exit(1)


class SimpleAutoGenAgent:
    """简化的 AutoGen 代理示例"""
    
    def __init__(self, name: str, system_message: str):
        self.name = name
        self.system_message = system_message
        self.human_input_mode = "NEVER"
        self.max_consecutive_auto_reply = 3
    
    async def generate_reply(self, messages: list, turn: int = 0) -> str:
        """模拟 AutoGen 代理生成回复"""
        await asyncio.sleep(0.3)  # 模拟处理时间
        
        if "user_proxy" in self.name.lower():
            responses = [
                "我来协调这次讨论，确保我们充分解决您的问题。",
                "基于前面的分析，我认为我们还需要考虑实际实施的可行性。",
                "让我总结一下各位专家的意见，形成一个综合的解决方案。"
            ]
            return responses[min(turn, len(responses) - 1)]
        elif "assistant" in self.name.lower():
            responses = [
                "我来提供详细的技术分析。首先，我们需要明确需求和约束条件。",
                "基于第一轮分析，我补充一些技术细节和最佳实践建议。",
                "综合考虑各方面因素，我给出最终的技术建议和实施步骤。"
            ]
            return responses[min(turn, len(responses) - 1)]
        elif "reviewer" in self.name.lower() or "critic" in self.name.lower():
            responses = [
                "作为审查员，我需要指出这个方案的潜在风险和改进空间。",
                "从质量保证角度，我补充一些测试和验证的建议。",
                "最后，我确认这个方案已经经过充分的讨论和优化。"
            ]
            return responses[min(turn, len(responses) - 1)]
        else:
            return f"从{self.name}的角度，我认为这是一个值得深入探讨的话题。"


class AutoGenGroupChatDemo:
    """AutoGen 群聊演示类"""
    
    def __init__(self, agents: list):
        self.agents = agents
        self.encoder = EventEncoder()
        
    async def emit_event(self, event):
        """发送事件（演示用途，直接打印）"""
        encoded = self.encoder.encode(event)
        print(encoded.strip())
    
    async def run_group_chat(self, user_message: str):
        """运行 AutoGen 群聊"""
        run_id = str(uuid.uuid4())
        
        print("🤖 开始 AutoGen 群聊...")
        print("=" * 50)
        
        # 发送运行开始事件
        await self.emit_event(RunStartedEvent(
            thread_id="groupchat",
            run_id=run_id
        ))
        
        # 初始化群聊
        await self.emit_event(StepStartedEvent(
            step_name="initializing_group_chat"
        ))
        
        # 进行多轮对话
        total_turns = 3
        
        for turn in range(total_turns):
            print(f"\n--- 第 {turn + 1} 轮对话 ---")
            
            for i, agent in enumerate(self.agents):
                # 发送代理步骤开始事件
                step_name = f"agent_{agent.name}_turn_{turn+1}"
                await self.emit_event(StepStartedEvent(step_name=step_name))
                
                # 获取代理回复
                if turn == 0 and i == 0:
                    prompt_messages = [{"role": "user", "content": user_message}]
                else:
                    prompt_messages = [{"role": "system", "content": "继续群聊讨论"}]
                
                response = await agent.generate_reply(prompt_messages, turn)
                
                # 发送消息事件
                message_id = str(uuid.uuid4())
                
                await self.emit_event(TextMessageStartEvent(
                    message_id=message_id,
                    role="assistant"
                ))
                
                await self.emit_event(TextMessageContentEvent(
                    message_id=message_id,
                    delta=f"**{agent.name}** (轮次 {turn + 1}): {response}"
                ))
                
                await self.emit_event(TextMessageEndEvent(
                    message_id=message_id
                ))
                
                # 发送步骤结束事件
                await self.emit_event(StepFinishedEvent(step_name=step_name))
                
                # 代理间延迟
                await asyncio.sleep(0.3)
            
            # 轮次间延迟
            if turn < total_turns - 1:
                await asyncio.sleep(0.5)
        
        # 群聊总结
        await self.emit_event(StepFinishedEvent(
            step_name="initializing_group_chat"
        ))
        
        # 发送总结消息
        summary_id = str(uuid.uuid4())
        await self.emit_event(TextMessageStartEvent(
            message_id=summary_id,
            role="assistant"
        ))
        
        await self.emit_event(TextMessageContentEvent(
            message_id=summary_id,
            delta="🎯 **群聊总结**: 各位代理已完成讨论。每个代理都从自己的专业角度提供了见解和建议。"
        ))
        
        await self.emit_event(TextMessageEndEvent(
            message_id=summary_id
        ))
        
        # 发送运行结束事件
        await self.emit_event(RunFinishedEvent(
            thread_id="groupchat",
            run_id=run_id
        ))
        
        print("=" * 50)
        print("✅ 群聊完成！")


async def main():
    """主函数"""
    print("🚀 AG-UI + AutoGen 集成演示")
    print("")
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  提示: 未找到 OPENAI_API_KEY 环境变量")
        print("   这个演示使用模拟响应，实际集成时请设置你的 OpenAI API 密钥")
        print("")
    
    # 创建 AutoGen 代理
    agents = [
        SimpleAutoGenAgent(
            name="user_proxy",
            system_message="你是对话协调员，负责引导讨论进程"
        ),
        SimpleAutoGenAgent(
            name="technical_assistant", 
            system_message="你是技术助手，提供专业的技术分析和建议"
        ),
        SimpleAutoGenAgent(
            name="code_reviewer",
            system_message="你是代码审查员，关注代码质量和最佳实践"
        )
    ]
    
    # 创建群聊
    group_chat = AutoGenGroupChatDemo(agents)
    
    # 运行群聊
    user_question = "请帮我设计一个可扩展的微服务架构，包括服务发现、负载均衡和监控。"
    await group_chat.run_group_chat(user_question)


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())