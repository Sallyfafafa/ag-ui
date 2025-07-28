import { BaseEvent, EventType, AGUIError } from "@ag-ui/core";
import { Observable, throwError, of } from "rxjs";
import { mergeMap } from "rxjs/operators";

export const verifyEvents =
  (debug: boolean) =>
  (source$: Observable<BaseEvent>): Observable<BaseEvent> => {
    // Declare variables in closure to maintain state across events
    let activeMessageId: string | undefined;
    let activeToolCallIds: Set<string> = new Set(); // Track multiple tool calls
    let activeParallelId: string | undefined;
    let runFinished = false;
    let runError = false; // New flag to track if RUN_ERROR has been sent
    // New flags to track first/last event requirements
    let firstEventReceived = false;
    // Track active steps
    let activeSteps = new Map<string, boolean>(); // Map of step name -> active status
    let activeThinkingStep = false;
    let activeThinkingStepMessage = false;

    return source$.pipe(
      // Process each event through our state machine
      mergeMap((event) => {
        const eventType = event.type;

        if (debug) {
          console.debug("[VERIFY]:", JSON.stringify(event));
        }

        // Check if run has errored
        if (runError) {
          return throwError(
            () =>
              new AGUIError(
                `Cannot send event type '${eventType}': The run has already errored with 'RUN_ERROR'. No further events can be sent.`,
              ),
          );
        }

        // Check if run has already finished
        if (runFinished && eventType !== EventType.RUN_ERROR) {
          return throwError(
            () =>
              new AGUIError(
                `Cannot send event type '${eventType}': The run has already finished with 'RUN_FINISHED'. Start a new run with 'RUN_STARTED'.`,
              ),
          );
        }

        // Forbid lifecycle events and tool events inside a text message
        if (activeMessageId !== undefined) {
          // Define allowed event types inside a text message
          const allowedEventTypes = [
            EventType.TEXT_MESSAGE_CONTENT,
            EventType.TEXT_MESSAGE_END,
            EventType.RAW,
          ];

          // If the event type is not in the allowed list, throw an error
          if (!allowedEventTypes.includes(eventType)) {
            return throwError(
              () =>
                new AGUIError(
                  `Cannot send event type '${eventType}' after 'TEXT_MESSAGE_START': Send 'TEXT_MESSAGE_END' first.`,
                ),
            );
          }
        }

        // Forbid lifecycle events and text message events inside a tool call
        if (activeToolCallIds.size > 0 || activeParallelId !== undefined) {
          // Define allowed event types inside a tool call
          const allowedEventTypes = [
            EventType.TOOL_CALL_ARGS,
            EventType.TOOL_CALL_END,
            EventType.TOOL_CALL_START, // Allow multiple tool calls within parallel group
            EventType.PARALLEL_TOOL_CALLS_END,
            EventType.RAW,
          ];

          // If the event type is not in the allowed list, throw an error
          if (!allowedEventTypes.includes(eventType)) {
            // Special handling for nested tool calls in non-parallel mode for better error message
            if (eventType === EventType.TOOL_CALL_START && activeParallelId === undefined) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TOOL_CALL_START' event: A tool call is already in progress. Complete it with 'TOOL_CALL_END' first, or start a parallel group with 'PARALLEL_TOOL_CALLS_START'.`,
                  ),
              );
            }

            const contextMessage = activeParallelId !== undefined 
              ? `Send 'PARALLEL_TOOL_CALLS_END' first.`
              : `Send 'TOOL_CALL_END' first.`;

            return throwError(
              () =>
                new AGUIError(
                  `Cannot send event type '${eventType}' after 'TOOL_CALL_START': ${contextMessage}`,
                ),
            );
          }
        }

        // Handle first event requirement and prevent multiple RUN_STARTED
        if (!firstEventReceived) {
          firstEventReceived = true;
          if (eventType !== EventType.RUN_STARTED && eventType !== EventType.RUN_ERROR) {
            return throwError(() => new AGUIError(`First event must be 'RUN_STARTED'`));
          }
        } else if (eventType === EventType.RUN_STARTED) {
          // Prevent multiple RUN_STARTED events
          return throwError(
            () =>
              new AGUIError(
                `Cannot send multiple 'RUN_STARTED' events: A 'RUN_STARTED' event was already sent. Each run must have exactly one 'RUN_STARTED' event at the beginning.`,
              ),
          );
        }

        // Validate event based on type and current state
        switch (eventType) {
          // Text message flow
          case EventType.TEXT_MESSAGE_START: {
            // Can't start a message if one is already in progress
            if (activeMessageId !== undefined) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TEXT_MESSAGE_START' event: A text message is already in progress. Complete it with 'TEXT_MESSAGE_END' first.`,
                  ),
              );
            }

            activeMessageId = (event as any).messageId;
            return of(event);
          }

          case EventType.TEXT_MESSAGE_CONTENT: {
            // Must be in a message and IDs must match
            if (activeMessageId === undefined) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TEXT_MESSAGE_CONTENT' event: No active text message found. Start a text message with 'TEXT_MESSAGE_START' first.`,
                  ),
              );
            }

            if ((event as any).messageId !== activeMessageId) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TEXT_MESSAGE_CONTENT' event: Message ID mismatch. The ID '${(event as any).messageId}' doesn't match the active message ID '${activeMessageId}'.`,
                  ),
              );
            }

            return of(event);
          }

          case EventType.TEXT_MESSAGE_END: {
            // Must be in a message and IDs must match
            if (activeMessageId === undefined) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TEXT_MESSAGE_END' event: No active text message found. A 'TEXT_MESSAGE_START' event must be sent first.`,
                  ),
              );
            }

            if ((event as any).messageId !== activeMessageId) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TEXT_MESSAGE_END' event: Message ID mismatch. The ID '${(event as any).messageId}' doesn't match the active message ID '${activeMessageId}'.`,
                  ),
              );
            }

            // Reset message state
            activeMessageId = undefined;
            return of(event);
          }

          // Tool call flow
          case EventType.TOOL_CALL_START: {
            const toolCallId = (event as any).toolCallId;
            
            // Can't start a tool call if one is already in progress (unless in parallel mode)
            if (activeToolCallIds.has(toolCallId)) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TOOL_CALL_START' event: Tool call '${toolCallId}' is already in progress.`,
                  ),
              );
            }

            // If not in parallel mode and there's already an active tool call, error
            if (activeParallelId === undefined && activeToolCallIds.size > 0) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TOOL_CALL_START' event: A tool call is already in progress. Complete it with 'TOOL_CALL_END' first, or start a parallel group with 'PARALLEL_TOOL_CALLS_START'.`,
                  ),
              );
            }

            activeToolCallIds.add(toolCallId);
            return of(event);
          }

          case EventType.TOOL_CALL_ARGS: {
            const toolCallId = (event as any).toolCallId;
            
            // Must be in a tool call and IDs must match
            if (!activeToolCallIds.has(toolCallId)) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TOOL_CALL_ARGS' event: Tool call '${toolCallId}' is not active. Start a tool call with 'TOOL_CALL_START' first.`,
                  ),
              );
            }

            return of(event);
          }

          case EventType.TOOL_CALL_END: {
            const toolCallId = (event as any).toolCallId;
            
            // Must be in a tool call and IDs must match
            if (!activeToolCallIds.has(toolCallId)) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'TOOL_CALL_END' event: Tool call '${toolCallId}' is not active. A 'TOOL_CALL_START' event must be sent first.`,
                  ),
              );
            }

            // Remove tool call from active set
            activeToolCallIds.delete(toolCallId);
            return of(event);
          }

          // Parallel tool call flow
          case EventType.PARALLEL_TOOL_CALLS_START: {
            const parallelId = (event as any).parallelId;
            const toolCallIds = (event as any).toolCallIds || [];
            
            // Can't start parallel tool calls if any tool calls are already active
            if (activeToolCallIds.size > 0) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'PARALLEL_TOOL_CALLS_START' event: Tool calls are already in progress. Complete them first.`,
                  ),
              );
            }

            // Can't start parallel tool calls if already in parallel mode
            if (activeParallelId !== undefined) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'PARALLEL_TOOL_CALLS_START' event: Parallel tool calls '${activeParallelId}' are already in progress.`,
                  ),
              );
            }

            activeParallelId = parallelId;
            return of(event);
          }

          case EventType.PARALLEL_TOOL_CALLS_END: {
            const parallelId = (event as any).parallelId;
            
            // Must be in parallel mode and IDs must match
            if (activeParallelId !== parallelId) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'PARALLEL_TOOL_CALLS_END' event: Parallel ID mismatch or no parallel tool calls active. Expected '${activeParallelId}', got '${parallelId}'.`,
                  ),
              );
            }

            // All tool calls within the parallel group must be finished
            if (activeToolCallIds.size > 0) {
              const activeCalls = Array.from(activeToolCallIds).join(", ");
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'PARALLEL_TOOL_CALLS_END' event: Some tool calls are still active: ${activeCalls}. Complete them with 'TOOL_CALL_END' first.`,
                  ),
              );
            }

            // Reset parallel state
            activeParallelId = undefined;
            return of(event);
          }

          // Step flow
          case EventType.STEP_STARTED: {
            const stepName = (event as any).stepName;
            if (activeSteps.has(stepName)) {
              return throwError(
                () => new AGUIError(`Step "${stepName}" is already active for 'STEP_STARTED'`),
              );
            }
            activeSteps.set(stepName, true);
            return of(event);
          }

          case EventType.STEP_FINISHED: {
            const stepName = (event as any).stepName;
            if (!activeSteps.has(stepName)) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'STEP_FINISHED' for step "${stepName}" that was not started`,
                  ),
              );
            }
            activeSteps.delete(stepName);
            return of(event);
          }

          // Run flow
          case EventType.RUN_STARTED: {
            // We've already validated this above
            return of(event);
          }

          case EventType.RUN_FINISHED: {
            // Can't be the first event (already checked)
            // and can't happen after already being finished (already checked)

            // Check that all steps are finished before run ends
            if (activeSteps.size > 0) {
              const unfinishedSteps = Array.from(activeSteps.keys()).join(", ");
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'RUN_FINISHED' while steps are still active: ${unfinishedSteps}`,
                  ),
              );
            }

            runFinished = true;
            return of(event);
          }

          case EventType.RUN_ERROR: {
            // RUN_ERROR can happen at any time
            runError = true; // Set flag to prevent any further events
            return of(event);
          }

          case EventType.CUSTOM: {
            return of(event);
          }

          // Text message flow
          case EventType.THINKING_TEXT_MESSAGE_START: {
            if (!activeThinkingStep) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'THINKING_TEXT_MESSAGE_START' event: A thinking step is not in progress. Create one with 'THINKING_START' first.`,
                  ),
              );
            }
            // Can't start a message if one is already in progress
            if (activeThinkingStepMessage) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'THINKING_TEXT_MESSAGE_START' event: A thinking message is already in progress. Complete it with 'THINKING_TEXT_MESSAGE_END' first.`,
                  ),
              );
            }

            activeThinkingStepMessage = true;
            return of(event);
          }

          case EventType.THINKING_TEXT_MESSAGE_CONTENT: {
            // Must be in a message and IDs must match
            if (!activeThinkingStepMessage) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'THINKING_TEXT_MESSAGE_CONTENT' event: No active thinking message found. Start a message with 'THINKING_TEXT_MESSAGE_START' first.`,
                  ),
              );
            }

            return of(event);
          }

          case EventType.THINKING_TEXT_MESSAGE_END: {
            // Must be in a message and IDs must match
            if (!activeThinkingStepMessage) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'THINKING_TEXT_MESSAGE_END' event: No active thinking message found. A 'THINKING_TEXT_MESSAGE_START' event must be sent first.`,
                  ),
              );
            }

            // Reset message state
            activeThinkingStepMessage = false;
            return of(event);
          }

          case EventType.THINKING_START: {
            if (activeThinkingStep) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'THINKING_START' event: A thinking step is already in progress. End it with 'THINKING_END' first.`,
                  ),
              );
            }

            activeThinkingStep = true;
            return of(event);
          }

          case EventType.THINKING_END: {
            // Must be in a message and IDs must match
            if (!activeThinkingStep) {
              return throwError(
                () =>
                  new AGUIError(
                    `Cannot send 'THINKING_END' event: No active thinking step found. A 'THINKING_START' event must be sent first.`,
                  ),
              );
            }

            // Reset message state
            activeThinkingStep = false;
            return of(event);
          }

          default: {
            return of(event);
          }
        }
      }),
    );
  };
