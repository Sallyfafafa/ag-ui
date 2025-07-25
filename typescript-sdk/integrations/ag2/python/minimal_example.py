#!/usr/bin/env python3
"""
最小的 AG2 集成示例

这个示例展示了如何使用 AG-UI 与 AG2 集成的最简单方法。
运行这个脚本，你将看到两个 AG2 代理之间的对话。
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


class SimpleAG2Agent:
    """简化的 AG2 代理示例"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    async def generate_response(self, prompt: str) -> str:
        """模拟 AG2 代理生成响应"""
        await asyncio.sleep(0.2)  # 模拟处理时间
        
        if "助手" in self.role or "assistant" in self.role.lower():
            return f"作为{self.role}，我认为{prompt}是一个很好的问题。让我来详细分析一下相关的技术要点和最佳实践。"
        elif "分析师" in self.role or "analyst" in self.role.lower():
            return f"从{self.role}的角度来看，我需要指出几个关键考虑因素，包括性能、可维护性和安全性方面的影响。"
        else:
            return f"作为{self.role}，我想补充一些实际应用中的经验和建议。"


class AG2FlowDemo:
    """AG2 流程演示类"""
    
    def __init__(self, agents: list):
        self.agents = agents
        self.encoder = EventEncoder()
        
    async def emit_event(self, event):
        """发送事件（演示用途，直接打印）"""
        encoded = self.encoder.encode(event)
        print(encoded.strip())
    
    async def run_conversation(self, user_message: str):
        """运行多代理对话"""
        run_id = str(uuid.uuid4())
        
        print("🤖 开始 AG2 多代理对话...")
        print("=" * 50)
        
        # 发送运行开始事件
        await self.emit_event(RunStartedEvent(
            thread_id="demo",
            run_id=run_id
        ))
        
        conversation_history = []
        
        for i, agent in enumerate(self.agents):
            # 发送步骤开始事件
            await self.emit_event(StepStartedEvent(
                step_name=f"agent_{agent.name}_thinking"
            ))
            
            # 确定提示词
            if i == 0:
                prompt = user_message
            else:
                prev_response = conversation_history[-1] if conversation_history else ""
                prompt = f"基于前面的讨论：{prev_response}，请提供你的观点。"
            
            # 获取代理响应
            response = await agent.generate_response(prompt)
            conversation_history.append(response)
            
            # 发送消息事件
            message_id = str(uuid.uuid4())
            
            await self.emit_event(TextMessageStartEvent(
                message_id=message_id,
                role="assistant"
            ))
            
            await self.emit_event(TextMessageContentEvent(
                message_id=message_id,
                delta=f"**{agent.name}**: {response}"
            ))
            
            await self.emit_event(TextMessageEndEvent(
                message_id=message_id
            ))
            
            # 发送步骤结束事件
            await self.emit_event(StepFinishedEvent(
                step_name=f"agent_{agent.name}_thinking"
            ))
            
            # 添加延迟以模拟真实对话
            await asyncio.sleep(0.5)
        
        # 发送运行结束事件
        await self.emit_event(RunFinishedEvent(
            thread_id="demo",
            run_id=run_id
        ))
        
        print("=" * 50)
        print("✅ 对话完成！")


async def main():
    """主函数"""
    print("🚀 AG-UI + AG2 集成演示")
    print("")
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  提示: 未找到 OPENAI_API_KEY 环境变量")
        print("   这个演示使用模拟响应，实际集成时请设置你的 OpenAI API 密钥")
        print("")
    
    # 创建 AG2 代理
    agents = [
        SimpleAG2Agent("智能助手", "技术助手"),
        SimpleAG2Agent("代码分析师", "代码分析师"),
        SimpleAG2Agent("架构师", "系统架构师")
    ]
    
    # 创建对话流程
    flow = AG2FlowDemo(agents)
    
    # 运行对话
    user_question = "我想用 Python 构建一个高性能的 Web API，应该考虑哪些技术栈和架构设计？"
    await flow.run_conversation(user_question)


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())