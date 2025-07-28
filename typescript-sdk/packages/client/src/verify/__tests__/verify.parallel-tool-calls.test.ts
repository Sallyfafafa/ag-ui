import { Subject } from "rxjs";
import { toArray, catchError } from "rxjs/operators";
import { firstValueFrom } from "rxjs";
import { verifyEvents } from "../verify";
import {
  BaseEvent,
  EventType,
  AGUIError,
  RunStartedEvent,
  RunFinishedEvent,
  ToolCallStartEvent,
  ToolCallArgsEvent,
  ToolCallEndEvent,
  ParallelToolCallsStartEvent,
  ParallelToolCallsEndEvent,
} from "@ag-ui/core";

describe("verifyEvents parallel tool calls", () => {
  // Test: Should allow parallel tool calls
  it("should allow parallel tool calls within a parallel group", async () => {
    const source$ = new Subject<BaseEvent>();

    // Set up subscription and collect events
    const promise = firstValueFrom(
      verifyEvents(false)(source$).pipe(
        toArray(),
        catchError((err) => {
          throw err;
        }),
      ),
    );

    // Send a valid sequence with parallel tool calls
    source$.next({
      type: EventType.RUN_STARTED,
      threadId: "test-thread-id",
      runId: "test-run-id",
    } as RunStartedEvent);
    
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-1",
      toolCallIds: ["tool-1", "tool-2"],
    } as ParallelToolCallsStartEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-1",
      toolCallName: "test-tool-1",
    } as ToolCallStartEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-2",
      toolCallName: "test-tool-2",
    } as ToolCallStartEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: "tool-1",
      delta: "args for tool 1",
    } as ToolCallArgsEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_ARGS,
      toolCallId: "tool-2",
      delta: "args for tool 2",
    } as ToolCallArgsEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_END,
      toolCallId: "tool-1",
    } as ToolCallEndEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_END,
      toolCallId: "tool-2",
    } as ToolCallEndEvent);
    
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_END,
      parallelId: "parallel-1",
    } as ParallelToolCallsEndEvent);
    
    source$.next({ type: EventType.RUN_FINISHED } as RunFinishedEvent);

    // Complete the source
    source$.complete();

    // Await the promise and expect no errors
    const result = await promise;

    // Verify all events were processed
    expect(result.length).toBe(10);
    expect(result[1].type).toBe(EventType.PARALLEL_TOOL_CALLS_START);
    expect(result[2].type).toBe(EventType.TOOL_CALL_START);
    expect(result[3].type).toBe(EventType.TOOL_CALL_START);
    expect(result[8].type).toBe(EventType.PARALLEL_TOOL_CALLS_END);
  });

  // Test: Should not allow starting parallel tool calls when tool calls are active
  it("should not allow starting parallel tool calls when tool calls are active", async () => {
    const source$ = new Subject<BaseEvent>();
    const events: BaseEvent[] = [];

    // Create a subscription that will complete only after an error
    const subscription = verifyEvents(false)(source$).subscribe({
      next: (event) => events.push(event),
      error: (err) => {
        expect(err).toBeInstanceOf(AGUIError);
        expect(err.message).toContain(
          "Cannot send 'PARALLEL_TOOL_CALLS_START' event: Tool calls are already in progress",
        );
        subscription.unsubscribe();
      },
    });

    // Start a valid run and a single tool call
    source$.next({
      type: EventType.RUN_STARTED,
      threadId: "test-thread-id",
      runId: "test-run-id",
    } as RunStartedEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-1",
      toolCallName: "test-tool",
    } as ToolCallStartEvent);

    // Try to start parallel tool calls while a tool call is active
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-1",
      toolCallIds: ["tool-2", "tool-3"],
    } as ParallelToolCallsStartEvent);

    // Complete the source and wait a bit for processing
    source$.complete();
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify only events before the error were processed
    expect(events.length).toBe(2);
    expect(events[1].type).toBe(EventType.TOOL_CALL_START);
  });

  // Test: Should not allow nested parallel tool calls
  it("should not allow nested parallel tool calls", async () => {
    const source$ = new Subject<BaseEvent>();
    const events: BaseEvent[] = [];

    // Create a subscription that will complete only after an error
    const subscription = verifyEvents(false)(source$).subscribe({
      next: (event) => events.push(event),
      error: (err) => {
        expect(err).toBeInstanceOf(AGUIError);
        expect(err.message).toContain(
          "Cannot send 'PARALLEL_TOOL_CALLS_START' event: Parallel tool calls",
        );
        subscription.unsubscribe();
      },
    });

    // Start a valid run and parallel tool calls
    source$.next({
      type: EventType.RUN_STARTED,
      threadId: "test-thread-id",
      runId: "test-run-id",
    } as RunStartedEvent);
    
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-1",
      toolCallIds: ["tool-1", "tool-2"],
    } as ParallelToolCallsStartEvent);

    // Try to start another parallel group
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-2",
      toolCallIds: ["tool-3", "tool-4"],
    } as ParallelToolCallsStartEvent);

    // Complete the source and wait a bit for processing
    source$.complete();
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify only events before the error were processed
    expect(events.length).toBe(2);
    expect(events[1].type).toBe(EventType.PARALLEL_TOOL_CALLS_START);
  });

  // Test: Should not allow ending parallel tool calls with active tool calls
  it("should not allow ending parallel tool calls with active tool calls", async () => {
    const source$ = new Subject<BaseEvent>();
    const events: BaseEvent[] = [];

    // Create a subscription that will complete only after an error
    const subscription = verifyEvents(false)(source$).subscribe({
      next: (event) => events.push(event),
      error: (err) => {
        expect(err).toBeInstanceOf(AGUIError);
        expect(err.message).toContain(
          "Cannot send 'PARALLEL_TOOL_CALLS_END' event: Some tool calls are still active",
        );
        subscription.unsubscribe();
      },
    });

    // Start a valid run, parallel tool calls, and some tool calls
    source$.next({
      type: EventType.RUN_STARTED,
      threadId: "test-thread-id",
      runId: "test-run-id",
    } as RunStartedEvent);
    
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-1",
      toolCallIds: ["tool-1", "tool-2"],
    } as ParallelToolCallsStartEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-1",
      toolCallName: "test-tool-1",
    } as ToolCallStartEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-2",
      toolCallName: "test-tool-2",
    } as ToolCallStartEvent);
    
    // End only one tool call, leaving the other active
    source$.next({
      type: EventType.TOOL_CALL_END,
      toolCallId: "tool-1",
    } as ToolCallEndEvent);

    // Try to end parallel tool calls while tool-2 is still active
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_END,
      parallelId: "parallel-1",
    } as ParallelToolCallsEndEvent);

    // Complete the source and wait a bit for processing
    source$.complete();
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify only events before the error were processed
    expect(events.length).toBe(5);
    expect(events[4].type).toBe(EventType.TOOL_CALL_END);
  });

  // Test: Should not allow single tool call when already in parallel mode without starting parallel group
  it("should provide helpful error when mixing single and parallel tool calls", async () => {
    const source$ = new Subject<BaseEvent>();
    const events: BaseEvent[] = [];

    // Create a subscription that will complete only after an error
    const subscription = verifyEvents(false)(source$).subscribe({
      next: (event) => events.push(event),
      error: (err) => {
        expect(err).toBeInstanceOf(AGUIError);
        expect(err.message).toContain(
          "A tool call is already in progress. Complete it with 'TOOL_CALL_END' first, or start a parallel group with 'PARALLEL_TOOL_CALLS_START'",
        );
        subscription.unsubscribe();
      },
    });

    // Start a valid run and a single tool call
    source$.next({
      type: EventType.RUN_STARTED,
      threadId: "test-thread-id",
      runId: "test-run-id",
    } as RunStartedEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-1",
      toolCallName: "test-tool",
    } as ToolCallStartEvent);

    // Try to start another tool call without parallel group
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-2",
      toolCallName: "test-tool-2",
    } as ToolCallStartEvent);

    // Complete the source and wait a bit for processing
    source$.complete();
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify only events before the error were processed
    expect(events.length).toBe(2);
    expect(events[1].type).toBe(EventType.TOOL_CALL_START);
  });

  // Test: Should not allow duplicate tool call IDs within parallel group
  it("should not allow duplicate tool call IDs", async () => {
    const source$ = new Subject<BaseEvent>();
    const events: BaseEvent[] = [];

    // Create a subscription that will complete only after an error
    const subscription = verifyEvents(false)(source$).subscribe({
      next: (event) => events.push(event),
      error: (err) => {
        expect(err).toBeInstanceOf(AGUIError);
        expect(err.message).toContain(
          "Tool call 'tool-1' is already in progress",
        );
        subscription.unsubscribe();
      },
    });

    // Start a valid run and parallel tool calls
    source$.next({
      type: EventType.RUN_STARTED,
      threadId: "test-thread-id",
      runId: "test-run-id",
    } as RunStartedEvent);
    
    source$.next({
      type: EventType.PARALLEL_TOOL_CALLS_START,
      parallelId: "parallel-1",
      toolCallIds: ["tool-1", "tool-2"],
    } as ParallelToolCallsStartEvent);
    
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-1",
      toolCallName: "test-tool-1",
    } as ToolCallStartEvent);

    // Try to start the same tool call ID again
    source$.next({
      type: EventType.TOOL_CALL_START,
      toolCallId: "tool-1",
      toolCallName: "test-tool-1-duplicate",
    } as ToolCallStartEvent);

    // Complete the source and wait a bit for processing
    source$.complete();
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Verify only events before the error were processed
    expect(events.length).toBe(3);
    expect(events[2].type).toBe(EventType.TOOL_CALL_START);
  });
});