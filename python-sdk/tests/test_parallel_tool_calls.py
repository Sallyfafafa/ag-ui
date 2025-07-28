"""Test parallel tool calls events."""

import pytest
from ag_ui.core.events import (
    EventType,
    ParallelToolCallsStartEvent,
    ParallelToolCallsEndEvent,
)


def test_parallel_tool_calls_start_event():
    """Test creating ParallelToolCallsStartEvent."""
    event = ParallelToolCallsStartEvent(
        parallel_id="parallel-1",
        tool_call_ids=["tool-1", "tool-2", "tool-3"],
        parent_message_id="msg-1",
    )
    
    assert event.type == EventType.PARALLEL_TOOL_CALLS_START
    assert event.parallel_id == "parallel-1"
    assert event.tool_call_ids == ["tool-1", "tool-2", "tool-3"]
    assert event.parent_message_id == "msg-1"


def test_parallel_tool_calls_end_event():
    """Test creating ParallelToolCallsEndEvent."""
    event = ParallelToolCallsEndEvent(
        parallel_id="parallel-1",
    )
    
    assert event.type == EventType.PARALLEL_TOOL_CALLS_END
    assert event.parallel_id == "parallel-1"


def test_parallel_tool_calls_start_event_validation():
    """Test ParallelToolCallsStartEvent validation."""
    # Should work without parent_message_id (optional)
    event = ParallelToolCallsStartEvent(
        parallel_id="parallel-1",
        tool_call_ids=["tool-1", "tool-2"],
    )
    
    assert event.type == EventType.PARALLEL_TOOL_CALLS_START
    assert event.parallel_id == "parallel-1"
    assert event.tool_call_ids == ["tool-1", "tool-2"]
    assert event.parent_message_id is None


def test_event_types_include_parallel_events():
    """Test that EventType includes parallel tool call types."""
    assert EventType.PARALLEL_TOOL_CALLS_START == "PARALLEL_TOOL_CALLS_START"
    assert EventType.PARALLEL_TOOL_CALLS_END == "PARALLEL_TOOL_CALLS_END"


def test_parallel_events_serialization():
    """Test that parallel events can be serialized and deserialized."""
    start_event = ParallelToolCallsStartEvent(
        parallel_id="parallel-1",
        tool_call_ids=["tool-1", "tool-2"],
        parent_message_id="msg-1",
    )
    
    # Test JSON serialization
    json_data = start_event.model_dump()
    expected_data = {
        "type": "PARALLEL_TOOL_CALLS_START",
        "parallelId": "parallel-1",  # CamelCase due to alias_generator
        "toolCallIds": ["tool-1", "tool-2"],
        "parentMessageId": "msg-1",
        "timestamp": None,
        "rawEvent": None,
    }
    
    assert json_data == expected_data
    
    # Test deserialization
    recreated_event = ParallelToolCallsStartEvent.model_validate(json_data)
    assert recreated_event.parallel_id == start_event.parallel_id
    assert recreated_event.tool_call_ids == start_event.tool_call_ids
    assert recreated_event.parent_message_id == start_event.parent_message_id