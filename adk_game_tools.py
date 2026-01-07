"""
Google ADK Game Tools: Rock-Paper-Scissors-Plus referee tools.

All tools are registered via @adk_tool decorator.
Tools are invoked only through ADK executor (ToolExecutor), not direct calls.
"""

from typing import Dict, Any
import json
from pathlib import Path

from adk_core import GameState, GAMESTATE_JSON_SCHEMA
from google.adk import tool


# ============================================================================
# ADK Tool #1: Load Game State (Read-Only Tool)
# ============================================================================

@tool(
    name="load_game_state",
    description="ADK read-only tool: load persistent GameState from storage",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "default": "game_state.json"}
        },
    },
    output_schema=GAMESTATE_JSON_SCHEMA,
)
def load_game_state(path: str = "game_state.json") -> dict:
    """Load GameState from JSON file and return as dict."""
    p = Path(path)
    if not p.exists():
        return GameState().to_dict()
    with p.open("r", encoding="utf-8") as f:
        return GameState.from_dict(json.load(f)).to_dict()


# ============================================================================
# ADK Tool #2: Update Game State (Mutation Tool)
# ============================================================================

@tool(
    name="update_game_state",
    description="ADK mutation tool: persist new GameState (SINGLE MUTATION POINT)",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "default": "game_state.json"},
            "round_number": {"type": "integer"},
            "user_score": {"type": "integer"},
            "bot_score": {"type": "integer"},
            "user_used_bomb": {"type": "boolean"},
            "bot_used_bomb": {"type": "boolean"},
        },
        "required": [
            "round_number",
            "user_score",
            "bot_score",
            "user_used_bomb",
            "bot_used_bomb",
        ],
    },
    output_schema=GAMESTATE_JSON_SCHEMA,
)
def update_game_state(
    path: str,
    round_number: int,
    user_score: int,
    bot_score: int,
    user_used_bomb: bool,
    bot_used_bomb: bool,
) -> dict:
    """Persist the provided GameState fields to storage, returning dict."""
    gs = GameState(
        round_number=round_number,
        user_score=user_score,
        bot_score=bot_score,
        user_used_bomb=user_used_bomb,
        bot_used_bomb=bot_used_bomb,
    )

    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(gs.to_dict(), f, indent=2)

    return gs.to_dict()


# ============================================================================
# ADK Tool #3: Validate Move (Validation Tool)
# ============================================================================

@tool(
    name="validate_move",
    description="ADK validation tool: check move legality",
    input_schema={
        "type": "object",
        "properties": {
            "move": {"type": ["string", "null"]},
            "user_used_bomb": {"type": "boolean"},
        },
        "required": ["move", "user_used_bomb"],
    },
    output_schema={
        "type": "object",
        "properties": {"is_valid": {"type": "boolean"}, "reason": {"type": "string"}},
        "required": ["is_valid", "reason"],
    },
)
def validate_move(move: str, user_used_bomb: bool) -> dict:
    """Validate a move against game rules, returning dict for ADK agent."""
    if move is None:
        return {"is_valid": False, "reason": "invalid"}
    try:
        s = str(move).strip().lower()
    except Exception:
        return {"is_valid": False, "reason": "invalid"}
    if s not in {"rock", "paper", "scissors", "bomb"}:
        return {"is_valid": False, "reason": "invalid"}
    if s == "bomb" and user_used_bomb:
        return {"is_valid": False, "reason": "bomb_already_used"}
    return {"is_valid": True, "reason": "ok"}


# ============================================================================
# ADK Tool #4: Resolve Round (Resolution Tool)
# ============================================================================

@tool(
    name="resolve_round",
    description="ADK resolution tool: deterministically resolve a round",
    input_schema={
        "type": "object",
        "properties": {"user_move": {"type": "string"}, "bot_move": {"type": "string"}},
        "required": ["user_move", "bot_move"],
    },
    output_schema={"type": "string", "enum": ["User wins", "Bot wins", "Draw", "Invalid"]},
)
def resolve_round(user_move: str, bot_move: str) -> str:
    """Resolve a round given two moves."""
    VALID_MOVES = {"rock", "paper", "scissors", "bomb"}
    RPS_BEATS = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

    if user_move not in VALID_MOVES or bot_move not in VALID_MOVES:
        return "Invalid"
    if user_move == bot_move:
        return "Draw"
    if user_move == "bomb" and bot_move == "bomb":
        return "Draw"
    if user_move == "bomb":
        return "User wins"
    if bot_move == "bomb":
        return "Bot wins"
    if RPS_BEATS.get(user_move) == bot_move:
        return "User wins"
    if RPS_BEATS.get(bot_move) == user_move:
        return "Bot wins"
    return "Invalid"


# ============================================================================
# ADK Tool #5: Reset Game State (Reset Tool)
# ============================================================================

@tool(
    name="reset_game_state",
    description="ADK reset tool: reset game to initial state",
    input_schema={"type": "object", "properties": {"path": {"type": "string", "default": "game_state.json"}}},
    output_schema=GAMESTATE_JSON_SCHEMA,
)
def reset_game_state(path: str = "game_state.json") -> dict:
    """Reset game to initial state via the single mutation tool."""
    fresh = GameState()
    return update_game_state(
        path=path,
        round_number=fresh.round_number,
        user_score=fresh.user_score,
        bot_score=fresh.bot_score,
        user_used_bomb=fresh.user_used_bomb,
        bot_used_bomb=fresh.bot_used_bomb,
    )


# Registry of all tools for easy Agent wiring.
GAME_TOOLS = [
    load_game_state,
    update_game_state,
    validate_move,
    resolve_round,
    reset_game_state,
]
