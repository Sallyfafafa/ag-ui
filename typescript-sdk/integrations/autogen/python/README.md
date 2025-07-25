# AG-UI AutoGen Integration

This package provides integration between AG-UI and AutoGen for building interactive multi-agent applications.

## Installation

```bash
pip install ag-ui-autogen
```

## Quick Start

```python
from ag_ui_autogen import AutoGenFlow
import autogen

# Configure AutoGen agents
config_list = [{"model": "gpt-4", "api_key": "your-api-key"}]

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list},
)

# Create and run the AG-UI flow
flow = AutoGenFlow(agents=[user_proxy, assistant])
await flow.start()
```

## Examples

See the `examples/` directory for complete working examples.

## Requirements

- Python 3.10+
- AutoGen (pyautogen)
- FastAPI
- Uvicorn