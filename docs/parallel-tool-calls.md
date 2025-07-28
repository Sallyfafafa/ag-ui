# Parallel Tool Calls Support

AG-UI now supports parallel tool calling, allowing agents to execute multiple tools concurrently rather than sequentially. This can significantly improve performance when multiple independent operations need to be performed.

## Overview

The parallel tool calls feature introduces two new event types:

- `PARALLEL_TOOL_CALLS_START`: Marks the beginning of a parallel tool execution group
- `PARALLEL_TOOL_CALLS_END`: Marks the end of a parallel tool execution group

Within a parallel group, multiple `TOOL_CALL_START`, `TOOL_CALL_ARGS`, and `TOOL_CALL_END` events can be sent concurrently.

## Event Flow

### Sequential Tool Calls (Existing Behavior)
```
RUN_STARTED
├── TOOL_CALL_START (tool-1)
├── TOOL_CALL_ARGS (tool-1)
├── TOOL_CALL_END (tool-1)
├── TOOL_CALL_START (tool-2)
├── TOOL_CALL_ARGS (tool-2)
└── TOOL_CALL_END (tool-2)
RUN_FINISHED
```

### Parallel Tool Calls (New Behavior)
```
RUN_STARTED
├── PARALLEL_TOOL_CALLS_START (parallel-1)
├── TOOL_CALL_START (tool-1)
├── TOOL_CALL_START (tool-2)
├── TOOL_CALL_ARGS (tool-1)
├── TOOL_CALL_ARGS (tool-2)
├── TOOL_CALL_END (tool-1)
├── TOOL_CALL_END (tool-2)
└── PARALLEL_TOOL_CALLS_END (parallel-1)
RUN_FINISHED
```

## TypeScript Example

```typescript
import { 
  EventType, 
  ParallelToolCallsStartEvent, 
  ParallelToolCallsEndEvent,
  ToolCallStartEvent,
  ToolCallArgsEvent,
  ToolCallEndEvent 
} from '@ag-ui/core';

// Start parallel tool execution
const parallelStart: ParallelToolCallsStartEvent = {
  type: EventType.PARALLEL_TOOL_CALLS_START,
  parallelId: 'weather-and-calendar',
  toolCallIds: ['get-weather', 'check-calendar'],
  parentMessageId: 'msg-123'
};

// Start individual tool calls
const weatherToolStart: ToolCallStartEvent = {
  type: EventType.TOOL_CALL_START,
  toolCallId: 'get-weather',
  toolCallName: 'get_current_weather',
  parentMessageId: 'msg-123'
};

const calendarToolStart: ToolCallStartEvent = {
  type: EventType.TOOL_CALL_START,
  toolCallId: 'check-calendar',
  toolCallName: 'check_calendar_events',
  parentMessageId: 'msg-123'
};

// Send arguments (can be interleaved)
const weatherArgs: ToolCallArgsEvent = {
  type: EventType.TOOL_CALL_ARGS,
  toolCallId: 'get-weather',
  delta: '{"location": "San Francisco"}'
};

const calendarArgs: ToolCallArgsEvent = {
  type: EventType.TOOL_CALL_ARGS,
  toolCallId: 'check-calendar',
  delta: '{"date": "2024-01-15"}'
};

// End tool calls (can complete in any order)
const weatherEnd: ToolCallEndEvent = {
  type: EventType.TOOL_CALL_END,
  toolCallId: 'get-weather'
};

const calendarEnd: ToolCallEndEvent = {
  type: EventType.TOOL_CALL_END,
  toolCallId: 'check-calendar'
};

// End parallel execution
const parallelEnd: ParallelToolCallsEndEvent = {
  type: EventType.PARALLEL_TOOL_CALLS_END,
  parallelId: 'weather-and-calendar'
};
```

## Python Example

```python
from ag_ui.core.events import (
    EventType,
    ParallelToolCallsStartEvent,
    ParallelToolCallsEndEvent,
    ToolCallStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent
)

# Start parallel tool execution
parallel_start = ParallelToolCallsStartEvent(
    parallel_id="weather-and-calendar",
    tool_call_ids=["get-weather", "check-calendar"],
    parent_message_id="msg-123"
)

# Start individual tool calls
weather_tool_start = ToolCallStartEvent(
    tool_call_id="get-weather",
    tool_call_name="get_current_weather",
    parent_message_id="msg-123"
)

calendar_tool_start = ToolCallStartEvent(
    tool_call_id="check-calendar",
    tool_call_name="check_calendar_events",
    parent_message_id="msg-123"
)

# Send arguments
weather_args = ToolCallArgsEvent(
    tool_call_id="get-weather",
    delta='{"location": "San Francisco"}'
)

calendar_args = ToolCallArgsEvent(
    tool_call_id="check-calendar", 
    delta='{"date": "2024-01-15"}'
)

# End tool calls
weather_end = ToolCallEndEvent(tool_call_id="get-weather")
calendar_end = ToolCallEndEvent(tool_call_id="check-calendar")

# End parallel execution
parallel_end = ParallelToolCallsEndEvent(
    parallel_id="weather-and-calendar"
)
```

## Rules and Constraints

1. **Parallel Group Isolation**: Only one parallel group can be active at a time
2. **Sequential vs Parallel**: Cannot mix sequential and parallel tool calls - must choose one approach per execution
3. **Complete Before End**: All tool calls within a parallel group must be completed before sending `PARALLEL_TOOL_CALLS_END`
4. **Unique Tool Call IDs**: Each tool call within a parallel group must have a unique ID
5. **Backward Compatibility**: Existing sequential tool call behavior remains unchanged

## Error Cases

### Starting Parallel While Tool Call Active
```typescript
// ❌ This will error
emit(toolCallStart);        // Start single tool call
emit(parallelStart);        // ERROR: Tool calls already in progress
```

### Ending Parallel With Active Tool Calls
```typescript
// ❌ This will error  
emit(parallelStart);        // Start parallel group
emit(toolCallStart1);       // Start tool call 1
emit(toolCallStart2);       // Start tool call 2
emit(toolCallEnd1);         // End tool call 1
emit(parallelEnd);          // ERROR: tool call 2 still active
```

### Nested Parallel Groups
```typescript
// ❌ This will error
emit(parallelStart1);       // Start parallel group 1
emit(parallelStart2);       // ERROR: Nested parallel groups not allowed
```

## Migration Guide

Existing code using sequential tool calls will continue to work without changes:

```typescript
// ✅ This still works (sequential)
emit(toolCallStart1);
emit(toolCallArgs1);
emit(toolCallEnd1);
emit(toolCallStart2);
emit(toolCallArgs2);
emit(toolCallEnd2);
```

To upgrade to parallel tool calls:

```typescript
// ✅ Upgraded to parallel
emit(parallelStart);
emit(toolCallStart1);
emit(toolCallStart2);
emit(toolCallArgs1);
emit(toolCallArgs2);
emit(toolCallEnd1);
emit(toolCallEnd2);
emit(parallelEnd);
```

## Performance Benefits

Parallel tool calls can provide significant performance improvements:

- **I/O-bound operations**: Web requests, database queries, file operations
- **Independent computations**: Multiple calculations that don't depend on each other
- **External service calls**: APIs, microservices, third-party integrations

Example scenario: Instead of waiting 2 seconds for weather + 2 seconds for calendar (4 total), parallel execution takes ~2 seconds total.