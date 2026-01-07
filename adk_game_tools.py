"""
Google ADK Game Tools: Rock-Paper-Scissors-Plus referee tools.

All tools are registered via @adk_tool decorator.
Tools are invoked only through ADK executor (ToolExecutor), not direct calls.
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass, asdict
import json
from pathlib import Path

import adk_core

try:
    import google_adk as gadk  # type: ignore
except Exception as e:
    raise ImportError(
        "google_adk not available. Install with: pip install google-adk"
    ) from e

GAMESTATE_JSON_SCHEMA = adk_core.GAMESTATE_JSON_SCHEMA


# ============================================================================
# GameState Dataclass
# ============================================================================

@dataclass
class GameState:
    """ADK GameState object (conforms to GAMESTATE_JSON_SCHEMA)."""
    round_number: int = 0
    user_score: int = 0
    bot_score: int = 0
    user_used_bomb: bool = False
    bot_used_bomb: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "GameState":
        return GameState(
            round_number=d.get("round_number", 0),
            user_score=d.get("user_score", 0),
            bot_score=d.get("bot_score", 0),
            user_used_bomb=d.get("user_used_bomb", False),
            bot_used_bomb=d.get("bot_used_bomb", False),
        )


# ============================================================================
# ADK Tool #1: Load Game State (Read-Only Tool)
# ============================================================================

@gadk.tool(
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
def load_game_state(path: str = "game_state.json") -> GameState:
    """Load GameState from JSON file."""
    p = Path(path)
    if not p.exists():
        return GameState()
    with p.open("r", encoding="utf-8") as f:
        return GameState.from_dict(json.load(f))


# ============================================================================
# ADK Tool #2: Update Game State (Mutation Tool)
# ============================================================================

@gadk.tool(
    name="update_game_state",
    description="ADK mutation tool: apply delta to GameState and persist (SINGLE MUTATION POINT)",
    input_schema={
        "type": "object",
        "properties": {
            "state": {"type": "object"},
            "deltas": {
                "type": "object",
                "properties": {
                    "round_increment": {"type": "integer"},
                    "user_score_delta": {"type": "integer"},
                    "bot_score_delta": {"type": "integer"},
                    "user_used_bomb": {"type": "boolean"},
                    "bot_used_bomb": {"type": "boolean"},
                },
            },
            "path": {"type": "string", "default": "game_state.json"},
        },
        "required": ["state", "deltas"],
    },
    output_schema=GAMESTATE_JSON_SCHEMA,
)
def update_game_state(state: dict, deltas: dict, path: str = "game_state.json") -> GameState:
    """Apply deltas to GameState and persist to storage."""
    # Reconstruct GameState from dict
    gs = GameState.from_dict(state)
    
    # Apply deltas
    gs.round_number += int(deltas.get("round_increment", 0))
    gs.user_score += int(deltas.get("user_score_delta", 0))
    gs.bot_score += int(deltas.get("bot_score_delta", 0))
    
    if "user_used_bomb" in deltas:
        gs.user_used_bomb = bool(deltas["user_used_bomb"])
    if "bot_used_bomb" in deltas:
        gs.bot_used_bomb = bool(deltas["bot_used_bomb"])
    
    # Persist
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(gs.to_dict(), f, indent=2)
    
    return gs


# ============================================================================
# ADK Tool #3: Validate Move (Validation Tool)
# ============================================================================

@gadk.tool(
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
def validate_move(move: str, user_used_bomb: bool) -> Tuple[bool, str]:
    """Validate a move against game rules."""
    if move is None:
        return False, "invalid"
    try:
        s = str(move).strip().lower()
    except Exception:
        return False, "invalid"
    if s not in {"rock", "paper", "scissors", "bomb"}:
        return False, "invalid"
    if s == "bomb" and user_used_bomb:
        return False, "bomb_already_used"
    return True, "ok"


# ============================================================================
# ADK Tool #4: Resolve Round (Resolution Tool)
# ============================================================================

@gadk.tool(
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

@gadk.tool(
    name="reset_game_state",
    description="ADK reset tool: reset game to initial state",
    input_schema={"type": "object", "properties": {"path": {"type": "string", "default": "game_state.json"}}},
    output_schema=GAMESTATE_JSON_SCHEMA,
)
def reset_game_state(path: str = "game_state.json") -> GameState:
    """Reset game to initial state."""
    fresh = GameState()
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(fresh.to_dict(), f, indent=2)
    return fresh
