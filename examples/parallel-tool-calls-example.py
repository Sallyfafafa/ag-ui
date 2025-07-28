#!/usr/bin/env python3
"""
Example demonstrating parallel tool calls using AG-UI Python SDK.

This example shows how to use the new parallel tool calls feature to execute
multiple tools concurrently instead of sequentially.
"""

from ag_ui.core.events import (
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
)


def sequential_tool_calls_example():
    """Example of sequential tool calls (existing behavior)."""
    print("=== Sequential Tool Calls Example ===")
    
    events = [
        RunStartedEvent(thread_id="thread-1", run_id="run-1"),
        
        TextMessageStartEvent(message_id="msg-1", role="assistant"),
        TextMessageContentEvent(message_id="msg-1", delta="I'll check the weather and your calendar for you."),
        TextMessageEndEvent(message_id="msg-1"),
        
        # First tool call (weather)
        ToolCallStartEvent(
            tool_call_id="weather-1",
            tool_call_name="get_current_weather",
            parent_message_id="msg-1"
        ),
        ToolCallArgsEvent(tool_call_id="weather-1", delta='{"location": "San Francisco", "unit": "celsius"}'),
        ToolCallEndEvent(tool_call_id="weather-1"),
        ToolCallResultEvent(
            message_id="msg-2",
            tool_call_id="weather-1",
            content="Current weather in San Francisco: 18°C, partly cloudy"
        ),
        
        # Second tool call (calendar)
        ToolCallStartEvent(
            tool_call_id="calendar-1",
            tool_call_name="check_calendar_events",
            parent_message_id="msg-1"
        ),
        ToolCallArgsEvent(tool_call_id="calendar-1", delta='{"date": "2024-01-15", "timezone": "PST"}'),
        ToolCallEndEvent(tool_call_id="calendar-1"),
        ToolCallResultEvent(
            message_id="msg-3",
            tool_call_id="calendar-1",
            content="You have 2 meetings today: 10 AM team standup, 2 PM client call"
        ),
        
        TextMessageStartEvent(message_id="msg-4", role="assistant"),
        TextMessageContentEvent(
            message_id="msg-4",
            delta="Based on the weather and your calendar, I recommend bringing a light jacket for your meetings today."
        ),
        TextMessageEndEvent(message_id="msg-4"),
        
        RunFinishedEvent(thread_id="thread-1", run_id="run-1")
    ]
    
    for i, event in enumerate(events, 1):
        print(f"{i:2d}. {event.type}: {event.model_dump(exclude={'timestamp', 'raw_event', 'type'})}")


def parallel_tool_calls_example():
    """Example of parallel tool calls (new feature)."""
    print("\n=== Parallel Tool Calls Example ===")
    
    events = [
        RunStartedEvent(thread_id="thread-2", run_id="run-2"),
        
        TextMessageStartEvent(message_id="msg-1", role="assistant"),
        TextMessageContentEvent(message_id="msg-1", delta="I'll check the weather and your calendar simultaneously."),
        TextMessageEndEvent(message_id="msg-1"),
        
        # Start parallel tool execution
        ParallelToolCallsStartEvent(
            parallel_id="weather-and-calendar",
            tool_call_ids=["weather-2", "calendar-2"],
            parent_message_id="msg-1"
        ),
        
        # Start both tool calls (can be in any order)
        ToolCallStartEvent(
            tool_call_id="weather-2",
            tool_call_name="get_current_weather",
            parent_message_id="msg-1"
        ),
        ToolCallStartEvent(
            tool_call_id="calendar-2", 
            tool_call_name="check_calendar_events",
            parent_message_id="msg-1"
        ),
        
        # Send arguments (can be interleaved)
        ToolCallArgsEvent(tool_call_id="weather-2", delta='{"location": "San Francisco"'),
        ToolCallArgsEvent(tool_call_id="calendar-2", delta='{"date": "2024-01-15"'),
        ToolCallArgsEvent(tool_call_id="weather-2", delta=', "unit": "celsius"}'),
        ToolCallArgsEvent(tool_call_id="calendar-2", delta=', "timezone": "PST"}'),
        
        # End tool calls (can complete in any order)
        ToolCallEndEvent(tool_call_id="calendar-2"),  # Calendar finishes first
        ToolCallEndEvent(tool_call_id="weather-2"),   # Weather finishes second
        
        # Results can come in any order
        ToolCallResultEvent(
            message_id="msg-2",
            tool_call_id="calendar-2",
            content="You have 2 meetings today: 10 AM team standup, 2 PM client call"
        ),
        ToolCallResultEvent(
            message_id="msg-3",
            tool_call_id="weather-2",
            content="Current weather in San Francisco: 18°C, partly cloudy"
        ),
        
        # End parallel execution
        ParallelToolCallsEndEvent(parallel_id="weather-and-calendar"),
        
        TextMessageStartEvent(message_id="msg-4", role="assistant"),
        TextMessageContentEvent(
            message_id="msg-4",
            delta="Perfect! I got both results simultaneously. Based on the weather and your calendar, I recommend bringing a light jacket for your meetings today."
        ),
        TextMessageEndEvent(message_id="msg-4"),
        
        RunFinishedEvent(thread_id="thread-2", run_id="run-2")
    ]
    
    for i, event in enumerate(events, 1):
        print(f"{i:2d}. {event.type}: {event.model_dump(exclude={'timestamp', 'raw_event', 'type'})}")


def complex_parallel_example():
    """Example with multiple parallel tool calls for a complex query."""
    print("\n=== Complex Parallel Tool Calls Example ===")
    
    events = [
        RunStartedEvent(thread_id="thread-3", run_id="run-3"),
        
        TextMessageStartEvent(message_id="msg-1", role="assistant"),
        TextMessageContentEvent(
            message_id="msg-1", 
            delta="I'll gather comprehensive information by checking weather, calendar, news, and traffic simultaneously."
        ),
        TextMessageEndEvent(message_id="msg-1"),
        
        # Start parallel execution with 4 tools
        ParallelToolCallsStartEvent(
            parallel_id="morning-briefing",
            tool_call_ids=["weather-3", "calendar-3", "news-3", "traffic-3"],
            parent_message_id="msg-1"
        ),
        
        # Start all tool calls
        ToolCallStartEvent(tool_call_id="weather-3", tool_call_name="get_current_weather"),
        ToolCallStartEvent(tool_call_id="calendar-3", tool_call_name="check_calendar_events"),
        ToolCallStartEvent(tool_call_id="news-3", tool_call_name="get_latest_news"),
        ToolCallStartEvent(tool_call_id="traffic-3", tool_call_name="check_traffic_conditions"),
        
        # Send arguments for all tools
        ToolCallArgsEvent(tool_call_id="weather-3", delta='{"location": "San Francisco"}'),
        ToolCallArgsEvent(tool_call_id="calendar-3", delta='{"date": "2024-01-15"}'),
        ToolCallArgsEvent(tool_call_id="news-3", delta='{"categories": ["tech", "business"]}'),
        ToolCallArgsEvent(tool_call_id="traffic-3", delta='{"route": "home to office"}'),
        
        # Tools complete in different order (simulating real async execution)
        ToolCallEndEvent(tool_call_id="news-3"),       # News finishes first (cached data)
        ToolCallEndEvent(tool_call_id="weather-3"),    # Weather finishes second
        ToolCallEndEvent(tool_call_id="traffic-3"),    # Traffic finishes third
        ToolCallEndEvent(tool_call_id="calendar-3"),   # Calendar finishes last
        
        # Results arrive as tools complete
        ToolCallResultEvent(
            message_id="msg-2",
            tool_call_id="news-3",
            content="Top tech news: AI breakthrough announced, new startup funding rounds"
        ),
        ToolCallResultEvent(
            message_id="msg-3",
            tool_call_id="weather-3",
            content="Current weather: 18°C, partly cloudy, light breeze"
        ),
        ToolCallResultEvent(
            message_id="msg-4",
            tool_call_id="traffic-3",
            content="Traffic conditions: Moderate traffic on I-101, expect 25-minute commute"
        ),
        ToolCallResultEvent(
            message_id="msg-5",
            tool_call_id="calendar-3",
            content="Today's schedule: 9 AM all-hands, 11 AM 1:1 with manager, 3 PM project review"
        ),
        
        # End parallel execution
        ParallelToolCallsEndEvent(parallel_id="morning-briefing"),
        
        TextMessageStartEvent(message_id="msg-6", role="assistant"),
        TextMessageContentEvent(
            message_id="msg-6",
            delta="Here's your morning briefing: Weather is pleasant (18°C), you have 3 meetings today, traffic is moderate (25 min), and there's exciting tech news. Perfect day ahead!"
        ),
        TextMessageEndEvent(message_id="msg-6"),
        
        RunFinishedEvent(thread_id="thread-3", run_id="run-3")
    ]
    
    for i, event in enumerate(events, 1):
        print(f"{i:2d}. {event.type}: {event.model_dump(exclude={'timestamp', 'raw_event', 'type'})}")


def main():
    """Run all examples."""
    print("AG-UI Parallel Tool Calls Examples")
    print("=" * 50)
    
    # Show sequential approach first
    sequential_tool_calls_example()
    
    # Show parallel approach
    parallel_tool_calls_example()
    
    # Show complex parallel scenario
    complex_parallel_example()
    
    print("\n" + "=" * 50)
    print("Key Benefits of Parallel Tool Calls:")
    print("• Reduced total execution time")
    print("• Better resource utilization") 
    print("• Improved user experience")
    print("• Maintained event ordering and validation")


if __name__ == "__main__":
    main()