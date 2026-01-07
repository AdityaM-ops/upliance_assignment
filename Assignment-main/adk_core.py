"""Core ADK types and schemas used by the local RPS+ referee.

This keeps a tiny, dependency-free definition of the GameState object and its
JSON schema so the project can run without the real Google ADK runtime.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any

# JSON schema describing the persisted game state structure.
GAMESTATE_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
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
}


@dataclass
class GameState:
    """Simple container for game state with helpers for (de)serialization."""

    round_number: int = 0
    user_score: int = 0
    bot_score: int = 0
    user_used_bomb: bool = False
    bot_used_bomb: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "GameState":
        return GameState(
            round_number=int(data.get("round_number", 0)),
            user_score=int(data.get("user_score", 0)),
            bot_score=int(data.get("bot_score", 0)),
            user_used_bomb=bool(data.get("user_used_bomb", False)),
            bot_used_bomb=bool(data.get("bot_used_bomb", False)),
        )
