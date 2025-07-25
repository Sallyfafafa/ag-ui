# AG-UI 工具定义模式详解

## 问题回答

针对您的问题"这个ag-ui 协议工具智能在前端定义吗？"，简短回答是：**不只是前端定义，AG-UI 支持多种工具定义模式**。

## 三种工具定义模式

### 1. 前端定义工具（标准模式）
- **位置**: 在前端应用中定义工具
- **执行**: 工具逻辑在前端执行
- **用途**: 用户交互、UI操作、人机协作
- **实现位置**: 
  - TypeScript: `typescript-sdk/apps/client-cli-example/src/tools/`
  - React: 使用 `useCopilotAction` hook

```typescript
// 示例：前端定义天气工具
export const weatherTool = createTool({
  id: "get-weather", 
  description: "获取天气信息",
  execute: async ({ context }) => {
    // 在前端执行
    return await getWeather(context.location);
  }
});
```

### 2. 后端定义工具
- **位置**: 在后端代理中定义和执行
- **执行**: 工具逻辑在服务器端执行  
- **用途**: 数据处理、密集计算、服务器资源操作
- **实现位置**: 
  - Python: `typescript-sdk/integrations/langgraph/python/ag_ui_langgraph/examples/agents/tool_based_generative_ui.py`
  - LangGraph: 使用 `bind_tools` 方法

```python
# 示例：后端定义俳句生成工具
GENERATE_HAIKU_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_haiku",
        "description": "生成日语俳句及其英语翻译",
        # 在服务器端执行
    }
}
```

### 3. 服务端作为客户端
- **位置**: 独立的服务作为客户端向代理注册工具
- **执行**: 在专业化的微服务中执行
- **用途**: 微服务架构、分布式工具生态系统
- **实现位置**: 新增的文档和示例 `docs/sdk/examples/server-as-client-tools.mdx`

```typescript
// 示例：通知服务提供工具
class NotificationToolProvider {
  async initialize() {
    await this.client.registerTools(tools, this.handleToolCall);
  }
}
```

## 在哪里实现的？

### 前端工具实现
1. **TypeScript 客户端**: `typescript-sdk/apps/client-cli-example/src/tools/`
2. **React 组件**: 使用 `@copilotkit/react-core` 的 `useCopilotAction`
3. **Mastra 框架**: 使用 `createTool` 函数

### 后端工具实现  
1. **Python 集成**: `typescript-sdk/integrations/*/python/` 各框架目录
2. **LangGraph**: `ag_ui_langgraph/examples/agents/`
3. **CrewAI**: `ag_ui_crewai/examples/`
4. **服务器启动器**: `server-starter-all-features/server/python/example_server/`

### 核心协议定义
1. **TypeScript 类型**: `typescript-sdk/packages/core/` 和 `packages/client/`
2. **Python 类型**: `python-sdk/ag_ui/core/types.py`
3. **事件协议**: `packages/proto/` protobuf 定义

## 选择建议

| 场景 | 推荐模式 | 原因 |
|------|----------|------|
| 用户确认操作 | 前端定义 | 需要直接UI交互 |
| 大数据处理 | 后端定义 | 计算密集，需要服务器资源 |
| 微服务架构 | 服务端作为客户端 | 服务解耦，专业化 |
| 实时协作 | 前端定义 | 需要即时用户反馈 |
| 安全敏感操作 | 后端定义 | 需要服务器端控制 |

## 总结

AG-UI 的设计理念是**灵活性和互操作性**：

- **不限制**工具只能在前端定义
- **支持**前端、后端、微服务等多种定义模式
- **允许**根据具体用例选择最合适的模式
- **提供**统一的协议确保不同模式之间的兼容性

这种设计使得 AG-UI 能够适应从简单的单页应用到复杂的分布式系统等各种架构需求。