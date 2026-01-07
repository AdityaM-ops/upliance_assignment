from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple
import json
from pathlib import Path


# ============================================================================
# ADK Schema Registration (Explicit Google ADK Primitives)
# ============================================================================

GAMESTATE_SCHEMA = {
    "name": "GameState",
    "type": "object",
    "properties": {
        "round_number": {"type": "integer", "description": "Current round (0-3)"},
        "user_score": {"type": "integer", "description": "User wins so far"},
        "bot_score": {"type": "integer", "description": "Bot wins so far"},
        "user_used_bomb": {"type": "boolean", "description": "User bomb consumed"},
        "bot_used_bomb": {"type": "boolean", "description": "Bot bomb consumed"},
    },
    "required": ["round_number", "user_score", "bot_score", "user_used_bomb", "bot_used_bomb"],
}

UPDATE_GAME_STATE_TOOL_SCHEMA = {
    "name": "update_game_state",
    "description": "ADK mutation tool: apply delta dict to GameState and persist.",
    "input_schema": {
        "type": "object",
        "properties": {
            "state": {"type": "object", "description": "Current GameState"},
            "deltas": {
                "type": "object",
                "description": "Delta dict with keys: round_increment, user_score_delta, bot_score_delta, user_used_bomb, bot_used_bomb",
                "properties": {
                    "round_increment": {"type": "integer"},
                    "user_score_delta": {"type": "integer"},
                    "bot_score_delta": {"type": "integer"},
                    "user_used_bomb": {"type": "boolean"},
                    "bot_used_bomb": {"type": "boolean"},
                },
            },
            "path": {"type": "string", "description": "Path to game_state.json"},
        },
        "required": ["state", "deltas"],
    },
    "output_schema": GAMESTATE_SCHEMA,
}

VALIDATE_MOVE_TOOL_SCHEMA = {
    "name": "validate_move_tool",
    "description": "ADK validation tool: check move legality.",
    "input_schema": {
        "type": "object",
        "properties": {
            "move": {"type": ["string", "null"]},
            "used_bomb": {"type": "boolean"},
        },
        "required": ["move", "used_bomb"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "is_valid": {"type": "boolean"},
            "reason": {"type": "string"},
        },
    },
}

RESOLVE_ROUND_TOOL_SCHEMA = {
    "name": "resolve_round_tool",
    "description": "ADK resolution tool: deterministically resolve round outcome.",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_move": {"type": "string", "enum": ["rock", "paper", "scissors", "bomb"]},
            "bot_move": {"type": "string", "enum": ["rock", "paper", "scissors", "bomb"]},
        },
        "required": ["user_move", "bot_move"],
    },
    "output_schema": {
        "type": "string",
        "enum": ["User wins", "Bot wins", "Draw", "Invalid"],
    },
}


# ============================================================================
# ADK DataClass & Tool Implementations
# ============================================================================
@dataclass
class GameState:
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


# Tool contract: load_game_state
def load_game_state(path: str = "game_state.json") -> GameState:
    """ADK tool: read-only tool that returns the current GameState.

    Schema (GameState): {
      round_number: int,
      user_score: int,
      bot_score: int,
      user_used_bomb: bool,
      bot_used_bomb: bool
    }
    """
    p = Path(path)
    if not p.exists():
        return GameState()
    with p.open("r", encoding="utf-8") as f:
        return GameState.from_dict(json.load(f))


# Tool contract: update_game_state
def update_game_state(state: GameState, deltas: Dict[str, Any], path: str = "game_state.json") -> GameState:
    """ADK tool: mutate and persist GameState.

    Acceptable delta keys:
      - "round_increment" (int)
      - "user_score_delta" (int)
      - "bot_score_delta" (int)
      - "user_used_bomb" (bool)
      - "bot_used_bomb" (bool)

    Returns: new GameState (post-apply)
    """
    # Apply deltas safely
    rn_inc = int(deltas.get("round_increment", 0))
    state.round_number += rn_inc

    state.user_score += int(deltas.get("user_score_delta", 0))
    state.bot_score += int(deltas.get("bot_score_delta", 0))

    if "user_used_bomb" in deltas:
        state.user_used_bomb = bool(deltas["user_used_bomb"])
    if "bot_used_bomb" in deltas:
        state.bot_used_bomb = bool(deltas["bot_used_bomb"])

    # Persist
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2)

    return state


# Tool contract: validate_move_tool
def validate_move_tool(move: Any, used_bomb: bool) -> Tuple[bool, str]:
    """ADK tool: validates a candidate move.

    Returns (is_valid, reason)
    Schema: input move: string|null, used_bomb: bool
    """
    if move is None:
        return False, "invalid"
    try:
        s = str(move).strip().lower()
    except Exception:
        return False, "invalid"
    if s not in {"rock", "paper", "scissors", "bomb"}:
        return False, "invalid"
    if s == "bomb" and used_bomb:
        return False, "bomb_already_used"
    return True, "ok"


# Tool contract: resolve_round_tool
def resolve_round_tool(user_move: str, bot_move: str) -> str:
    """ADK tool: deterministically resolve a round given normalized moves.

    Returns: one of 'User wins', 'Bot wins', 'Draw', 'Invalid'
    """
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


# Tool contract: reset_game_state
def reset_game_state(path: str = "game_state.json") -> GameState:
    """ADK tool: reset game to initial state and persist.

    Returns: fresh GameState with all counters at 0 and bombs unused.
    """
    fresh = GameState()
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(fresh.to_dict(), f, indent=2)
    return fresh


# ============================================================================
# Google ADK Agent (Explicit Schema Registration & Tool Binding)
# ============================================================================

class RockPaperScissorsPlusAgent:
    """Google ADK agent for Rock-Paper-Scissors-Plus referee.
    
    Registers GameState schema and tool contracts explicitly.
    Demonstrates proper ADK primitives:
    - schema registration (GAMESTATE_SCHEMA, tool schemas)
    - read-only tool (load_game_state)
    - mutation tool (update_game_state)
    - validator tool (validate_move_tool)
    - resolver tool (resolve_round_tool)
    """
    
    # Register schemas on class definition
    SCHEMAS = {
        "GameState": GAMESTATE_SCHEMA,
        "tools": {
            "update_game_state": UPDATE_GAME_STATE_TOOL_SCHEMA,
            "validate_move_tool": VALIDATE_MOVE_TOOL_SCHEMA,
            "resolve_round_tool": RESOLVE_ROUND_TOOL_SCHEMA,
        }
    }
    
    @staticmethod
    def invoke_load_tool(path: str = "game_state.json") -> GameState:
        """Invoke read-only tool: load_game_state."""
        return load_game_state(path)
    
    @staticmethod
    def invoke_validate_tool(move: Any, used_bomb: bool) -> Tuple[bool, str]:
        """Invoke validation tool: validate_move_tool."""
        return validate_move_tool(move, used_bomb)
    
    @staticmethod
    def invoke_resolve_tool(user_move: str, bot_move: str) -> str:
        """Invoke resolution tool: resolve_round_tool."""
        return resolve_round_tool(user_move, bot_move)
    
    @staticmethod
    def invoke_update_tool(state: GameState, deltas: Dict[str, Any], path: str = "game_state.json") -> GameState:
        """Invoke mutation tool: update_game_state (single mutation point)."""
        return update_game_state(state, deltas, path)
    
    @staticmethod
    def invoke_reset_tool(path: str = "game_state.json") -> GameState:
        """Invoke reset tool: reset_game_state."""
        return reset_game_state(path)

