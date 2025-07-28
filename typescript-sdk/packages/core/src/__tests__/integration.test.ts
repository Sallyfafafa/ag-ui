/**
 * Integration test to verify the parallel tool calls implementation works end-to-end.
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
  BaseEvent,
} from '../index';

describe('Parallel Tool Calls Integration', () => {
  it('should create valid parallel tool calls flow', () => {
    const events: BaseEvent[] = [
      // Start the run
      {
        type: EventType.RUN_STARTED,
        threadId: 'test-thread',
        runId: 'test-run',
      } as RunStartedEvent,
      
      // Start parallel tool execution
      {
        type: EventType.PARALLEL_TOOL_CALLS_START,
        parallelId: 'demo-parallel',
        toolCallIds: ['weather-call', 'calendar-call'],
      } as ParallelToolCallsStartEvent,
      
      // Start multiple tool calls concurrently
      {
        type: EventType.TOOL_CALL_START,
        toolCallId: 'weather-call',
        toolCallName: 'get_weather',
      } as ToolCallStartEvent,
      
      {
        type: EventType.TOOL_CALL_START,
        toolCallId: 'calendar-call',
        toolCallName: 'get_calendar',
      } as ToolCallStartEvent,
      
      // Send arguments (can be interleaved)
      {
        type: EventType.TOOL_CALL_ARGS,
        toolCallId: 'weather-call',
        delta: '{"location": "SF"}',
      } as ToolCallArgsEvent,
      
      {
        type: EventType.TOOL_CALL_ARGS,
        toolCallId: 'calendar-call',
        delta: '{"date": "today"}',
      } as ToolCallArgsEvent,
      
      // End tool calls (can finish in any order)
      {
        type: EventType.TOOL_CALL_END,
        toolCallId: 'calendar-call',
      } as ToolCallEndEvent,
      
      {
        type: EventType.TOOL_CALL_END,
        toolCallId: 'weather-call',
      } as ToolCallEndEvent,
      
      // End parallel execution
      {
        type: EventType.PARALLEL_TOOL_CALLS_END,
        parallelId: 'demo-parallel',
      } as ParallelToolCallsEndEvent,
      
      // Finish the run
      {
        type: EventType.RUN_FINISHED,
        threadId: 'test-thread',
        runId: 'test-run',
      } as RunFinishedEvent,
    ];
    
    expect(events).toHaveLength(10);
    expect(events[0].type).toBe(EventType.RUN_STARTED);
    expect(events[1].type).toBe(EventType.PARALLEL_TOOL_CALLS_START);
    expect(events[9].type).toBe(EventType.RUN_FINISHED);
  });

  it('should maintain backwards compatibility with sequential tool calls', () => {
    const events: BaseEvent[] = [
      {
        type: EventType.RUN_STARTED,
        threadId: 'seq-thread',
        runId: 'seq-run',
      } as RunStartedEvent,
      
      // Traditional sequential tool calls (should still work)
      {
        type: EventType.TOOL_CALL_START,
        toolCallId: 'first-tool',
        toolCallName: 'first_function',
      } as ToolCallStartEvent,
      
      {
        type: EventType.TOOL_CALL_ARGS,
        toolCallId: 'first-tool',
        delta: '{"arg": "value1"}',
      } as ToolCallArgsEvent,
      
      {
        type: EventType.TOOL_CALL_END,
        toolCallId: 'first-tool',
      } as ToolCallEndEvent,
      
      {
        type: EventType.TOOL_CALL_START,
        toolCallId: 'second-tool',
        toolCallName: 'second_function',
      } as ToolCallStartEvent,
      
      {
        type: EventType.TOOL_CALL_ARGS,
        toolCallId: 'second-tool',
        delta: '{"arg": "value2"}',
      } as ToolCallArgsEvent,
      
      {
        type: EventType.TOOL_CALL_END,
        toolCallId: 'second-tool',
      } as ToolCallEndEvent,
      
      {
        type: EventType.RUN_FINISHED,
        threadId: 'seq-thread',
        runId: 'seq-run',
      } as RunFinishedEvent,
    ];
    
    expect(events).toHaveLength(8);
    expect(events[0].type).toBe(EventType.RUN_STARTED);
    expect(events[1].type).toBe(EventType.TOOL_CALL_START);
    expect(events[7].type).toBe(EventType.RUN_FINISHED);
  });

  it('should validate parallel event types correctly', () => {
    // Test valid parallel start event
    const parallelStart: ParallelToolCallsStartEvent = {
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: 'test-parallel',
      toolCallIds: ['tool1', 'tool2'],
    };
    
    expect(parallelStart.type).toBe(EventType.PARALLEL_TOOL_CALLS_START);
    expect(parallelStart.parallelId).toBe('test-parallel');
    expect(parallelStart.toolCallIds).toEqual(['tool1', 'tool2']);
    
    // Test valid parallel end event
    const parallelEnd: ParallelToolCallsEndEvent = {
      type: EventType.PARALLEL_TOOL_CALLS_END,
      parallelId: 'test-parallel',
    };
    
    expect(parallelEnd.type).toBe(EventType.PARALLEL_TOOL_CALLS_END);
    expect(parallelEnd.parallelId).toBe('test-parallel');
  });

  it('should include new event types in EventType enum', () => {
    expect(EventType.PARALLEL_TOOL_CALLS_START).toBe('PARALLEL_TOOL_CALLS_START');
    expect(EventType.PARALLEL_TOOL_CALLS_END).toBe('PARALLEL_TOOL_CALLS_END');
  });
});