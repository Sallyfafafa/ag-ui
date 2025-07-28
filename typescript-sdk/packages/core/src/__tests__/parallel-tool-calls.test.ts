import {
  EventType,
  ParallelToolCallsStartEvent,
  ParallelToolCallsEndEvent,
  EventSchemas,
} from "../events";

describe("Parallel tool calls events", () => {
  it("should create valid ParallelToolCallsStartEvent", () => {
    const event: ParallelToolCallsStartEvent = {
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-1",
      toolCallIds: ["tool-1", "tool-2", "tool-3"],
      parentMessageId: "msg-1",
    };

    // Should validate successfully
    const result = EventSchemas.safeParse(event);
    expect(result.success).toBe(true);
    
    if (result.success) {
      expect(result.data.type).toBe(EventType.PARALLEL_TOOL_CALLS_START);
      expect(result.data.parallelId).toBe("parallel-1");
      expect(result.data.toolCallIds).toEqual(["tool-1", "tool-2", "tool-3"]);
      expect(result.data.parentMessageId).toBe("msg-1");
    }
  });

  it("should create valid ParallelToolCallsEndEvent", () => {
    const event: ParallelToolCallsEndEvent = {
      type: EventType.PARALLEL_TOOL_CALLS_END,
      parallelId: "parallel-1",
    };

    // Should validate successfully
    const result = EventSchemas.safeParse(event);
    expect(result.success).toBe(true);
    
    if (result.success) {
      expect(result.data.type).toBe(EventType.PARALLEL_TOOL_CALLS_END);
      expect(result.data.parallelId).toBe("parallel-1");
    }
  });

  it("should reject ParallelToolCallsStartEvent with missing fields", () => {
    const event = {
      type: EventType.PARALLEL_TOOL_CALLS_START,
      // Missing parallelId and toolCallIds
    };

    const result = EventSchemas.safeParse(event);
    expect(result.success).toBe(false);
  });

  it("should reject ParallelToolCallsEndEvent with missing fields", () => {
    const event = {
      type: EventType.PARALLEL_TOOL_CALLS_END,
      // Missing parallelId
    };

    const result = EventSchemas.safeParse(event);
    expect(result.success).toBe(false);
  });

  it("should include parallel tool call event types in enum", () => {
    expect(EventType.PARALLEL_TOOL_CALLS_START).toBe("PARALLEL_TOOL_CALLS_START");
    expect(EventType.PARALLEL_TOOL_CALLS_END).toBe("PARALLEL_TOOL_CALLS_END");
  });
});