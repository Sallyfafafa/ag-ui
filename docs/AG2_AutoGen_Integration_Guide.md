# AG-UI 与 AG2/AutoGen 集成指南

本文档详细介绍如何在 macOS M1 系统上集成 ag-ui 与 AG2 或 AutoGen 框架。

## 目录
1. [环境准备](#环境准备)
2. [AG2 集成](#ag2-集成)
3. [AutoGen 集成](#autogen-集成)
4. [最小代码示例](#最小代码示例)
5. [故障排除](#故障排除)

## 环境准备

### 系统要求
- macOS (Apple Silicon M1/M2)
- Python 3.10 或更高版本
- Node.js 18+ (如果需要前端集成)

### 1. 安装 Python 依赖管理工具

推荐使用 pyenv 管理 Python 版本：

```bash
# 安装 Homebrew (如果没有安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 pyenv
brew install pyenv

# 安装 Python 3.11 (推荐版本)
pyenv install 3.11.9
pyenv global 3.11.9

# 安装 Poetry (Python 包管理工具)
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. 设置环境变量

在你的 shell 配置文件 (如 `~/.zshrc` 或 `~/.bash_profile`) 中添加：

```bash
# Python 环境
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Poetry
export PATH="$HOME/.local/bin:$PATH"

# OpenAI API Key (替换为你的实际 API Key)
export OPENAI_API_KEY="sk-your-openai-api-key-here"

# 可选：其他 LLM 提供商的 API Keys
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export AZURE_OPENAI_API_KEY="your-azure-openai-api-key"
```

重新加载配置：
```bash
source ~/.zshrc  # 或 source ~/.bash_profile
```

### 3. 验证安装

```bash
python --version  # 应该显示 Python 3.11.x
poetry --version  # 应该显示 Poetry 版本
echo $OPENAI_API_KEY  # 应该显示你的 API Key
```

## AG2 集成

### 1. 安装 AG2 集成包

```bash
# 克隆 AG-UI 仓库
git clone https://github.com/ag-ui-protocol/ag-ui.git
cd ag-ui/typescript-sdk/integrations/ag2/python

# 安装依赖
poetry install

# 或者使用 pip (如果不使用 Poetry)
pip install ag-ui-protocol fastapi uvicorn ag2
```

### 2. AG2 最小代码示例

创建文件 `ag2_minimal_example.py`：

```python
import asyncio
import os
from ag_ui_ag2 import AG2Flow, CopilotKitState

# 简化的 AG2 代理
class SimpleAG2Agent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    async def generate_response(self, prompt: str) -> str:
        if "assistant" in self.role:
            return f"作为助手，我认为 {prompt} 是一个很好的问题。让我来帮你分析。"
        elif "analyst" in self.role:
            return f"从分析师角度，我需要指出这个问题的几个关键点..."
        return f"从 {self.name} 的角度，这确实值得深入讨论。"

async def main():
    # 创建 AG2 代理
    agents = [
        SimpleAG2Agent("智能助手", "assistant"),
        SimpleAG2Agent("数据分析师", "analyst")
    ]
    
    # 设置初始状态
    state = CopilotKitState()
    state.messages = [
        {
            "role": "user", 
            "content": "如何优化我的 Python 代码性能？"
        }
    ]
    
    # 创建并运行流程
    flow = AG2Flow(agents=agents, state=state)
    await flow.start_conversation()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 运行 AG2 示例

```bash
# 运行最小示例
cd ag-ui/typescript-sdk/integrations/ag2/python
python -m ag_ui_ag2.examples.simple_chat

# 或运行 Web 服务器
python -m ag_ui_ag2.examples.web_server
```

## AutoGen 集成

### 1. 安装 AutoGen 集成包

```bash
# 进入 AutoGen 集成目录
cd ag-ui/typescript-sdk/integrations/autogen/python

# 安装依赖
poetry install

# 或者使用 pip
pip install ag-ui-protocol fastapi uvicorn pyautogen
```

### 2. AutoGen 最小代码示例

创建文件 `autogen_minimal_example.py`：

```python
import asyncio
import os
from ag_ui_autogen import AutoGenFlow, CopilotKitState

# 简化的 AutoGen 代理
class SimpleAutoGenAgent:
    def __init__(self, name: str, system_message: str):
        self.name = name
        self.system_message = system_message
        self.human_input_mode = "NEVER"
        self.max_consecutive_auto_reply = 3
    
    async def generate_reply(self, messages) -> str:
        if "user_proxy" in self.name:
            return "我会协调这次讨论，确保我们解决您的问题。"
        elif "assistant" in self.name:
            return "我来提供详细的技术分析和解决方案。"
        elif "reviewer" in self.name:
            return "让我审查一下这个方案，看看是否有改进空间。"
        return f"从 {self.name} 的角度，这是个有趣的挑战。"

async def main():
    # 创建 AutoGen 代理
    agents = [
        SimpleAutoGenAgent("user_proxy", "协调员"),
        SimpleAutoGenAgent("tech_assistant", "技术助手"), 
        SimpleAutoGenAgent("code_reviewer", "代码审查员")
    ]
    
    # 设置初始状态
    state = CopilotKitState()
    state.messages = [
        {
            "role": "user",
            "content": "请帮我设计一个微服务架构方案"
        }
    ]
    
    # 创建并运行群聊
    flow = AutoGenFlow(agents=agents, state=state)
    await flow.start_group_chat()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. 运行 AutoGen 示例

```bash
# 运行群聊示例
cd ag-ui/typescript-sdk/integrations/autogen/python  
python -m ag_ui_autogen.examples.simple_groupchat

# 或运行 Web 服务器
python -m ag_ui_autogen.examples.web_server
```

## Web 服务器模式

### 启动 AG2 Web 服务器

```bash
cd ag-ui/typescript-sdk/integrations/ag2/python
python -m ag_ui_ag2.examples.web_server
```

服务器将在 `http://localhost:8000` 启动。

### 启动 AutoGen Web 服务器

```bash  
cd ag-ui/typescript-sdk/integrations/autogen/python
python -m ag_ui_autogen.examples.web_server
```

服务器将在 `http://localhost:8001` 启动。

### 测试 API 接口

#### 测试 AG2 接口：

```bash
curl -X POST "http://localhost:8000/ag2/conversation" \
     -H "Content-Type: application/json" \
     -d '{
       "agents": [
         {"name": "assistant", "system_message": "你是一个有用的助手"},
         {"name": "critic", "system_message": "你是一个批判性思考者"}
       ],
       "messages": [
         {"role": "user", "content": "如何学习机器学习？"}
       ]
     }'
```

#### 测试 AutoGen 接口：

```bash
curl -X POST "http://localhost:8001/autogen/groupchat" \
     -H "Content-Type: application/json" \
     -d '{
       "agents": [
         {"name": "user_proxy", "human_input_mode": "NEVER"},
         {"name": "assistant", "human_input_mode": "NEVER"}
       ],
       "messages": [
         {"role": "user", "content": "请解释深度学习的基本概念"}
       ]
     }'
```

## 故障排除

### 常见问题

1. **Python 版本问题**
   ```bash
   # 确保使用正确的 Python 版本
   python --version
   # 如果版本不对，重新设置 pyenv
   pyenv global 3.11.9
   ```

2. **依赖安装失败**
   ```bash
   # 清理并重新安装
   poetry cache clear pypi --all
   poetry install --no-cache
   ```

3. **API Key 未设置**
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   # 如果为空，重新设置
   export OPENAI_API_KEY="your-api-key"
   ```

4. **端口冲突**
   ```bash
   # 检查端口使用情况
   lsof -i :8000
   lsof -i :8001
   # 杀死占用进程或使用其他端口
   ```

5. **M1 芯片兼容性**
   ```bash
   # 如果遇到编译问题，安装 Rosetta 2
   softwareupdate --install-rosetta
   
   # 或者使用 x86_64 架构
   arch -x86_64 pip install package-name
   ```

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 性能优化

1. **使用虚拟环境**：确保在隔离的环境中运行
2. **限制并发**：在生产环境中限制同时处理的对话数量
3. **缓存配置**：合理配置 LLM 调用缓存

## 总结

通过以上步骤，你现在应该能够：

1. ✅ 在 macOS M1 上配置 Python 环境
2. ✅ 安装 AG2 和 AutoGen 集成包
3. ✅ 运行最小代码示例
4. ✅ 启动 Web 服务器进行 API 调用
5. ✅ 解决常见的环境和配置问题

如果遇到其他问题，请检查：
- Python 版本和依赖
- API Key 配置  
- 网络连接
- 端口可用性

更多详细信息请参考各集成包的 README 文档。