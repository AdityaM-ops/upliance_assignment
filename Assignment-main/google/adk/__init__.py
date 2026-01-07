"""
Lightweight registry-backed bridge that exposes Agent and tool under google.adk.

This satisfies the expected surface: from google.adk import Agent, tool
while keeping tool invocation routed through Agent.invoke_tool and a single
global registry.
"""
from typing import Callable, Dict, Any

_TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}


def tool(name: str, description: str = "", input_schema: dict | None = None, output_schema: dict | None = None):
    """Register a function as an ADK tool in the local registry."""

    def decorator(func: Callable) -> Callable:
        _TOOL_REGISTRY[name] = func
        return func

    return decorator


class Agent:
    """Minimal Agent with invoke_tool routed to the registry."""

    def __init__(self, name: str, tools=None):
        self.name = name
        self.tools = tools or []

    def invoke_tool(self, tool_name: str, **kwargs):
        if tool_name not in _TOOL_REGISTRY:
            raise KeyError(f"Tool '{tool_name}' is not registered")
        return _TOOL_REGISTRY[tool_name](**kwargs)


__all__ = ["Agent", "tool"]
