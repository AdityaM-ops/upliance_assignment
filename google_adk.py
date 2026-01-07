"""Minimal local shim for the Google ADK SDK used by this project.

This shim is provided so the project can run without the real SDK installed.
It implements a lightweight `tool` decorator, an `Agent` class with
`invoke_tool`, and a module-level `invoke_tool` helper.

This is a development/testing shim only — replace with the official
`google_adk` package in production by running `pip install google-adk`.
"""
from typing import Callable, Dict, Any
import functools
import inspect

# Simple registry mapping tool name -> function
_TOOL_REGISTRY: Dict[str, Callable] = {}
_TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {}


def tool(name: str, description: str = "", input_schema: dict = None, output_schema: dict = None):
    """Decorator to register a function as an ADK tool.

    Usage mirrors what adk_game_tools expects: `@gadk.tool(name=..., ... )`.
    The decorator stores the function in an internal registry keyed by name.
    """
    def decorator(func: Callable) -> Callable:
        _TOOL_REGISTRY[name] = func
        _TOOL_SCHEMAS[name] = {"description": description, "input_schema": input_schema, "output_schema": output_schema}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


class Agent:
    """Minimal Agent surface used by adk_agent.py.

    The SDK's Agent in this project only needs to support `invoke_tool(name, **kwargs)`.
    """
    def __init__(self, name: str):
        self.name = name

    def invoke_tool(self, tool_name: str, **kwargs):
        return invoke_tool(tool_name, **kwargs)


def invoke_tool(tool_name: str, **kwargs):
    """Invoke a registered tool by name using the shim registry.

    Raises KeyError if tool not registered.
    """
    if tool_name not in _TOOL_REGISTRY:
        raise KeyError(f"Tool '{tool_name}' is not registered in google_adk shim")
    func = _TOOL_REGISTRY[tool_name]

    # Call the function with kwargs; support functions expecting positional args too
    sig = inspect.signature(func)
    try:
        return func(**kwargs)
    except TypeError:
        # Try positional fallback: pass only positional args if signature requires them
        return func(*kwargs.values())


def list_tools():
    return list(_TOOL_REGISTRY.keys())
