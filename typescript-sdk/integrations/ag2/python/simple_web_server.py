#!/usr/bin/env python3
"""
AG2 Web Server 演示

这个脚本启动一个简单的 Web 服务器来演示 AG2 与 AG-UI 的集成。
访问 http://localhost:8000 查看 API 文档。
"""

import asyncio
import json
import sys
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

# 添加路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
ag_ui_root = os.path.join(os.path.dirname(project_root), '..', '..', '..', 'python-sdk')
sys.path.insert(0, ag_ui_root)

try:
    from ag_ui.core.events import (
        TextMessageStartEvent,
        TextMessageContentEvent, 
        TextMessageEndEvent,
        RunStartedEvent,
        RunFinishedEvent,
    )
    from ag_ui.encoder.encoder import EventEncoder
except ImportError as e:
    print(f"❌ 无法导入 ag-ui 库: {e}")
    sys.exit(1)


class AG2Agent(BaseModel):
    """AG2 代理模型"""
    name: str
    system_message: str


class ConversationRequest(BaseModel):
    """对话请求模型"""
    agents: List[AG2Agent]
    messages: List[Dict[str, Any]]


# 创建 FastAPI 应用
app = FastAPI(
    title="AG2 AG-UI 集成演示",
    description="展示 AG2 与 AG-UI 协议的集成",
    version="1.0.0"
)


async def simulate_ag2_conversation(agents: List[AG2Agent], user_message: str):
    """模拟 AG2 对话"""
    encoder = EventEncoder()
    run_id = str(uuid.uuid4())
    
    # 开始运行
    yield f"data: {encoder.encode(RunStartedEvent(thread_id='web', run_id=run_id))}"
    
    for i, agent in enumerate(agents):
        # 模拟代理响应
        if "assistant" in agent.name.lower():
            response = f"作为 {agent.name}，我认为这是一个很好的问题。让我来详细分析..."
        elif "critic" in agent.name.lower():
            response = f"从批判性角度，{agent.name} 指出一些需要注意的问题..."
        else:
            response = f"{agent.name} 提供了专业的见解和建议。"
        
        # 发送消息
        message_id = str(uuid.uuid4())
        
        yield f"data: {encoder.encode(TextMessageStartEvent(message_id=message_id, role='assistant'))}"
        yield f"data: {encoder.encode(TextMessageContentEvent(message_id=message_id, delta=f'**{agent.name}**: {response}'))}"
        yield f"data: {encoder.encode(TextMessageEndEvent(message_id=message_id))}"
        
        await asyncio.sleep(0.5)
    
    # 结束运行
    yield f"data: {encoder.encode(RunFinishedEvent(thread_id='web', run_id=run_id))}"


@app.post("/ag2/conversation")
async def start_ag2_conversation(request: ConversationRequest):
    """启动 AG2 对话"""
    try:
        # 获取用户消息
        user_messages = [msg for msg in request.messages if msg.get("role") == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="需要用户消息")
        
        user_message = user_messages[-1]["content"]
        
        return StreamingResponse(
            simulate_ag2_conversation(request.agents, user_message),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "AG2 Web Server 运行中！",
        "endpoints": {
            "conversation": "/ag2/conversation (POST)",
            "docs": "/docs"
        },
        "example_curl": """
curl -X POST "http://localhost:8000/ag2/conversation" \\
     -H "Content-Type: application/json" \\
     -d '{
       "agents": [
         {"name": "助手", "system_message": "你是一个有用的助手"},
         {"name": "分析师", "system_message": "你是一个批判性思考者"}
       ],
       "messages": [
         {"role": "user", "content": "如何学习 Python？"}
       ]
     }'
        """
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "ag2-integration"}


if __name__ == "__main__":
    print("🚀 启动 AG2 Web 服务器...")
    print("📖 访问 http://localhost:8000/docs 查看 API 文档")
    print("🔗 访问 http://localhost:8000 查看使用示例")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)