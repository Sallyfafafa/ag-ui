# AG-UI AG2 Integration

This package provides integration between AG-UI and AG2 (AutoGen 2.0) for building interactive multi-agent applications.

## Installation

```bash
pip install ag-ui-ag2
```

## Quick Start

```python
from ag_ui_ag2 import AG2Flow
from ag2 import Agent

# Create your AG2 agents
agents = [
    Agent(name="assistant", system_message="You are a helpful assistant"),
    Agent(name="critic", system_message="You are a critical reviewer")
]

# Create and run the AG-UI flow
flow = AG2Flow(agents=agents)
await flow.start()
```

## Examples

See the `examples/` directory for complete working examples.

## Requirements

- Python 3.10+
- AG2 (AutoGen 2.0)
- FastAPI
- Uvicorn