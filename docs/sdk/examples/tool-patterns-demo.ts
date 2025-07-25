/**
 * 实际可运行的 AG-UI 工具定义示例
 * Practical runnable AG-UI tool definition example
 */

// 前端定义工具示例 | Frontend-defined tools example
export const frontendToolExample = {
  // 在前端定义工具 | Define tools in frontend
  tools: [
    {
      name: "confirmUserAction",
      description: "请求用户确认操作 | Request user confirmation for action",
      parameters: {
        type: "object",
        properties: {
          action: {
            type: "string",
            description: "要确认的操作 | Action to confirm"
          },
          importance: {
            type: "string",
            enum: ["low", "medium", "high", "critical"],
            description: "重要程度 | Importance level"
          }
        },
        required: ["action"]
      }
    }
  ],
  
  // 工具处理器 | Tool handler
  handleTool: async (toolName: string, args: any) => {
    if (toolName === "confirmUserAction") {
      // 在前端处理用户确认 | Handle user confirmation in frontend
      const confirmed = await showConfirmDialog(args.action);
      return {
        confirmed,
        message: confirmed ? "用户已确认 | User confirmed" : "用户已取消 | User cancelled"
      };
    }
  }
};

// 后端定义工具示例 | Backend-defined tools example  
export const backendToolExample = {
  // 在后端定义工具 | Define tools in backend
  defineServerTools: () => [
    {
      name: "processData",
      description: "处理大量数据 | Process large amount of data",
      parameters: {
        type: "object",
        properties: {
          dataUrl: {
            type: "string",
            description: "数据源URL | Data source URL"
          },
          operation: {
            type: "string",
            enum: ["analyze", "transform", "summarize"],
            description: "处理操作 | Processing operation"
          }
        },
        required: ["dataUrl", "operation"]
      }
    }
  ],
  
  // 在服务器端执行 | Execute on server side
  executeServerTool: async (toolName: string, args: any) => {
    if (toolName === "processData") {
      // 在后端处理数据 | Process data on backend
      const result = await processLargeDataset(args.dataUrl, args.operation);
      return {
        success: true,
        result,
        processedAt: new Date().toISOString()
      };
    }
  }
};

// 服务端作为客户端示例 | Server-as-client example
export const serverAsClientExample = {
  // 服务提供者注册工具 | Service provider registers tools
  registerServiceTools: async (agentEndpoint: string) => {
    const client = new AgUiClient(agentEndpoint);
    
    const tools = [
      {
        name: "sendNotification",
        description: "发送通知 | Send notification",
        parameters: {
          type: "object",
          properties: {
            recipient: {
              type: "string",
              description: "接收者 | Recipient"
            },
            message: {
              type: "string", 
              description: "消息内容 | Message content"
            }
          },
          required: ["recipient", "message"]
        }
      }
    ];
    
    // 注册工具到代理 | Register tools with agent
    await client.registerTools(tools, async (toolName, args) => {
      if (toolName === "sendNotification") {
        // 服务端处理通知发送 | Server handles notification sending
        return await sendNotificationService(args.recipient, args.message);
      }
    });
  }
};

// 模拟函数 | Mock functions
async function showConfirmDialog(action: string): Promise<boolean> {
  // 在实际应用中，这里会显示UI确认对话框
  // In real app, this would show UI confirmation dialog
  return true;
}

async function processLargeDataset(url: string, operation: string): Promise<any> {
  // 在实际应用中，这里会处理大数据集
  // In real app, this would process large dataset
  return { processed: true, operation, url };
}

async function sendNotificationService(recipient: string, message: string): Promise<any> {
  // 在实际应用中，这里会发送真正的通知
  // In real app, this would send actual notification
  return { sent: true, recipient, message, sentAt: new Date().toISOString() };
}

// AG-UI 客户端模拟 | AG-UI client mock
class AgUiClient {
  constructor(private endpoint: string) {}
  
  async registerTools(tools: any[], handler: Function): Promise<void> {
    console.log(`工具已注册到 ${this.endpoint} | Tools registered to ${this.endpoint}`);
  }
}