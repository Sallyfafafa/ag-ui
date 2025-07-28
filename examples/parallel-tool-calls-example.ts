/**
 * Example demonstrating parallel tool calls using AG-UI TypeScript SDK.
 * 
 * This example shows how to use the new parallel tool calls feature to execute
 * multiple tools concurrently instead of sequentially.
 */

import {
  EventType,
  RunStartedEvent,
  RunFinishedEvent,
  ParallelToolCallsStartEvent,
  ParallelToolCallsEndEvent,
  ToolCallStartEvent,
  ToolCallArgsEvent,
  ToolCallEndEvent,
  ToolCallResultEvent,
  TextMessageStartEvent,
  TextMessageContentEvent,
  TextMessageEndEvent,
  BaseEvent,
} from '@ag-ui/core';

function sequentialToolCallsExample() {
  console.log('=== Sequential Tool Calls Example ===');
  
  const events: BaseEvent[] = [
    {
      type: EventType.RUN_STARTED,
      threadId: 'thread-1',
      runId: 'run-1',
    } as RunStartedEvent,
    
    {
      type: EventType.TEXT_MESSAGE_START,
      messageId: 'msg-1',
      role: 'assistant',
    } as TextMessageStartEvent,
    {
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId: 'msg-1',
      delta: "I'll check the weather and your calendar for you.",
    } as TextMessageContentEvent,
    {
      type: EventType.TEXT_MESSAGE_END,
      messageId: 'msg-1',
    } as TextMessageEndEvent,
    
    // First tool call (weather)
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'weather-1',
      toolCallName: 'get_current_weather',
      parentMessageId: 'msg-1',
    } as ToolCallStartEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'weather-1',
      delta: '{"location": "San Francisco", "unit": "celsius"}',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'weather-1',
    } as ToolCallEndEvent,
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-2',
      toolCallId: 'weather-1',
      content: 'Current weather in San Francisco: 18°C, partly cloudy',
    } as ToolCallResultEvent,
    
    // Second tool call (calendar)
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'calendar-1',
      toolCallName: 'check_calendar_events',
      parentMessageId: 'msg-1',
    } as ToolCallStartEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'calendar-1',
      delta: '{"date": "2024-01-15", "timezone": "PST"}',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'calendar-1',
    } as ToolCallEndEvent,
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-3',
      toolCallId: 'calendar-1',
      content: 'You have 2 meetings today: 10 AM team standup, 2 PM client call',
    } as ToolCallResultEvent,
    
    {
      type: EventType.TEXT_MESSAGE_START,
      messageId: 'msg-4',
      role: 'assistant',
    } as TextMessageStartEvent,
    {
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId: 'msg-4',
      delta: 'Based on the weather and your calendar, I recommend bringing a light jacket for your meetings today.',
    } as TextMessageContentEvent,
    {
      type: EventType.TEXT_MESSAGE_END,
      messageId: 'msg-4',
    } as TextMessageEndEvent,
    
    {
      type: EventType.RUN_FINISHED,
      threadId: 'thread-1',
      runId: 'run-1',
    } as RunFinishedEvent,
  ];
  
  events.forEach((event, i) => {
    const { type, timestamp, rawEvent, ...eventData } = event;
    console.log(`${(i + 1).toString().padStart(2)}. ${type}: ${JSON.stringify(eventData)}`);
  });
}

function parallelToolCallsExample() {
  console.log('\n=== Parallel Tool Calls Example ===');
  
  const events: BaseEvent[] = [
    {
      type: EventType.RUN_STARTED,
      threadId: 'thread-2',
      runId: 'run-2',
    } as RunStartedEvent,
    
    {
      type: EventType.TEXT_MESSAGE_START,
      messageId: 'msg-1',
      role: 'assistant',
    } as TextMessageStartEvent,
    {
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId: 'msg-1',
      delta: "I'll check the weather and your calendar simultaneously.",
    } as TextMessageContentEvent,
    {
      type: EventType.TEXT_MESSAGE_END,
      messageId: 'msg-1',
    } as TextMessageEndEvent,
    
    // Start parallel tool execution
    {
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: 'weather-and-calendar',
      toolCallIds: ['weather-2', 'calendar-2'],
      parentMessageId: 'msg-1',
    } as ParallelToolCallsStartEvent,
    
    // Start both tool calls (can be in any order)
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'weather-2',
      toolCallName: 'get_current_weather',
      parentMessageId: 'msg-1',
    } as ToolCallStartEvent,
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'calendar-2',
      toolCallName: 'check_calendar_events',
      parentMessageId: 'msg-1',
    } as ToolCallStartEvent,
    
    // Send arguments (can be interleaved)
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'weather-2',
      delta: '{"location": "San Francisco"',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'calendar-2',
      delta: '{"date": "2024-01-15"',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'weather-2',
      delta: ', "unit": "celsius"}',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'calendar-2',
      delta: ', "timezone": "PST"}',
    } as ToolCallArgsEvent,
    
    // End tool calls (can complete in any order)
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'calendar-2',
    } as ToolCallEndEvent, // Calendar finishes first
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'weather-2',
    } as ToolCallEndEvent, // Weather finishes second
    
    // Results can come in any order
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-2',
      toolCallId: 'calendar-2',
      content: 'You have 2 meetings today: 10 AM team standup, 2 PM client call',
    } as ToolCallResultEvent,
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-3',
      toolCallId: 'weather-2',
      content: 'Current weather in San Francisco: 18°C, partly cloudy',
    } as ToolCallResultEvent,
    
    // End parallel execution
    {
      type: EventType.PARALLEL_TOOL_CALLS_END,
      parallelId: 'weather-and-calendar',
    } as ParallelToolCallsEndEvent,
    
    {
      type: EventType.TEXT_MESSAGE_START,
      messageId: 'msg-4',
      role: 'assistant',
    } as TextMessageStartEvent,
    {
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId: 'msg-4',
      delta: 'Perfect! I got both results simultaneously. Based on the weather and your calendar, I recommend bringing a light jacket for your meetings today.',
    } as TextMessageContentEvent,
    {
      type: EventType.TEXT_MESSAGE_END,
      messageId: 'msg-4',
    } as TextMessageEndEvent,
    
    {
      type: EventType.RUN_FINISHED,
      threadId: 'thread-2',
      runId: 'run-2',
    } as RunFinishedEvent,
  ];
  
  events.forEach((event, i) => {
    const { type, timestamp, rawEvent, ...eventData } = event;
    console.log(`${(i + 1).toString().padStart(2)}. ${type}: ${JSON.stringify(eventData)}`);
  });
}

function complexParallelExample() {
  console.log('\n=== Complex Parallel Tool Calls Example ===');
  
  const events: BaseEvent[] = [
    {
      type: EventType.RUN_STARTED,
      threadId: 'thread-3',
      runId: 'run-3',
    } as RunStartedEvent,
    
    {
      type: EventType.TEXT_MESSAGE_START,
      messageId: 'msg-1',
      role: 'assistant',
    } as TextMessageStartEvent,
    {
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId: 'msg-1',
      delta: "I'll gather comprehensive information by checking weather, calendar, news, and traffic simultaneously.",
    } as TextMessageContentEvent,
    {
      type: EventType.TEXT_MESSAGE_END,
      messageId: 'msg-1',
    } as TextMessageEndEvent,
    
    // Start parallel execution with 4 tools
    {
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: 'morning-briefing',
      toolCallIds: ['weather-3', 'calendar-3', 'news-3', 'traffic-3'],
      parentMessageId: 'msg-1',
    } as ParallelToolCallsStartEvent,
    
    // Start all tool calls
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'weather-3',
      toolCallName: 'get_current_weather',
    } as ToolCallStartEvent,
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'calendar-3',
      toolCallName: 'check_calendar_events',
    } as ToolCallStartEvent,
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'news-3',
      toolCallName: 'get_latest_news',
    } as ToolCallStartEvent,
    {
      type: EventType.TOOL_CALL_START,
      toolCallId: 'traffic-3',
      toolCallName: 'check_traffic_conditions',
    } as ToolCallStartEvent,
    
    // Send arguments for all tools
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'weather-3',
      delta: '{"location": "San Francisco"}',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'calendar-3',
      delta: '{"date": "2024-01-15"}',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'news-3',
      delta: '{"categories": ["tech", "business"]}',
    } as ToolCallArgsEvent,
    {
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: 'traffic-3',
      delta: '{"route": "home to office"}',
    } as ToolCallArgsEvent,
    
    // Tools complete in different order (simulating real async execution)
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'news-3',
    } as ToolCallEndEvent, // News finishes first (cached data)
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'weather-3',
    } as ToolCallEndEvent, // Weather finishes second
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'traffic-3',
    } as ToolCallEndEvent, // Traffic finishes third
    {
      type: EventType.TOOL_CALL_END,
      toolCallId: 'calendar-3',
    } as ToolCallEndEvent, // Calendar finishes last
    
    // Results arrive as tools complete
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-2',
      toolCallId: 'news-3',
      content: 'Top tech news: AI breakthrough announced, new startup funding rounds',
    } as ToolCallResultEvent,
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-3',
      toolCallId: 'weather-3',
      content: 'Current weather: 18°C, partly cloudy, light breeze',
    } as ToolCallResultEvent,
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-4',
      toolCallId: 'traffic-3',
      content: 'Traffic conditions: Moderate traffic on I-101, expect 25-minute commute',
    } as ToolCallResultEvent,
    {
      type: EventType.TOOL_CALL_RESULT,
      messageId: 'msg-5',
      toolCallId: 'calendar-3',
      content: "Today's schedule: 9 AM all-hands, 11 AM 1:1 with manager, 3 PM project review",
    } as ToolCallResultEvent,
    
    // End parallel execution
    {
      type: EventType.PARALLEL_TOOL_CALLS_END,
      parallelId: 'morning-briefing',
    } as ParallelToolCallsEndEvent,
    
    {
      type: EventType.TEXT_MESSAGE_START,
      messageId: 'msg-6',
      role: 'assistant',
    } as TextMessageStartEvent,
    {
      type: EventType.TEXT_MESSAGE_CONTENT,
      messageId: 'msg-6',
      delta: "Here's your morning briefing: Weather is pleasant (18°C), you have 3 meetings today, traffic is moderate (25 min), and there's exciting tech news. Perfect day ahead!",
    } as TextMessageContentEvent,
    {
      type: EventType.TEXT_MESSAGE_END,
      messageId: 'msg-6',
    } as TextMessageEndEvent,
    
    {
      type: EventType.RUN_FINISHED,
      threadId: 'thread-3',
      runId: 'run-3',
    } as RunFinishedEvent,
  ];
  
  events.forEach((event, i) => {
    const { type, timestamp, rawEvent, ...eventData } = event;
    console.log(`${(i + 1).toString().padStart(2)}. ${type}: ${JSON.stringify(eventData)}`);
  });
}

function main() {
  console.log('AG-UI Parallel Tool Calls Examples');
  console.log('='.repeat(50));
  
  // Show sequential approach first
  sequentialToolCallsExample();
  
  // Show parallel approach
  parallelToolCallsExample();
  
  // Show complex parallel scenario
  complexParallelExample();
  
  console.log('\n' + '='.repeat(50));
  console.log('Key Benefits of Parallel Tool Calls:');
  console.log('• Reduced total execution time');
  console.log('• Better resource utilization');
  console.log('• Improved user experience');
  console.log('• Maintained event ordering and validation');
}

if (require.main === module) {
  main();
}

export {
  sequentialToolCallsExample,
  parallelToolCallsExample,
  complexParallelExample,
  main,
};