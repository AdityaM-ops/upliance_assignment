import random
from typing import Optional, Tuple

VALID_MOVES = {"rock", "paper", "scissors", "bomb"}
RPS_BEATS = {"rock": "scissors", "scissors": "paper", "paper": "rock"}


def interpret_intent(raw: str) -> Optional[str]:
    """Intent interpretation: normalize and validate raw input string.

    Returns normalized move (lowercase) or None for clearly invalid input.
    """
    if raw is None:
        return None
    s = raw.strip().lower()
    return s if s in VALID_MOVES else None


def validate_move(move: Optional[str], used_bomb: bool) -> Tuple[bool, Optional[str]]:
    """Rule validation: returns (is_valid, reason).

    An invalid move (including re-used bomb) is treated as invalid and wastes the round.
    """
    if move is None:
        return False, "invalid"
    if move == "bomb" and used_bomb:
        return False, "bomb_already_used"
    if move not in VALID_MOVES:
        return False, "invalid"
    return True, None


def generate_bot_move(bot_used_bomb: bool, round_number: int) -> str:
    """Deterministic bot move for reproducible runs.

    Strategy (deterministic):
    - Use a simple round-based selection: 0->rock,1->paper,2->scissors
    - If bot hasn't used bomb and round_number == 2, bot will play `bomb`.
    """
    if (not bot_used_bomb) and round_number % 3 == 2:
        return "bomb"
    order = ["rock", "paper", "scissors"]
    return order[round_number % 3]


def resolve_round(user_move: Optional[str], bot_move: Optional[str]) -> str:
    """Round resolution using internal comparison tables.

    Returns one of: 'User wins', 'Bot wins', 'Draw', 'Invalid'
    """
    # Invalid if either move is None or not recognized
    if user_move not in VALID_MOVES or bot_move not in VALID_MOVES:
        return "Invalid"

    if user_move == bot_move:
        return "Draw"

    # Bomb rules
    if user_move == "bomb" and bot_move == "bomb":
        return "Draw"
    if user_move == "bomb":
        return "User wins"
    if bot_move == "bomb":
        return "Bot wins"

    # Standard RPS table
    if RPS_BEATS.get(user_move) == bot_move:
        return "User wins"
    if RPS_BEATS.get(bot_move) == user_move:
        return "Bot wins"

    # Should not reach here, but treat as invalid
    return "Invalid"


def format_round_response(round_number: int, user_move: str, bot_move: str, result: str, user_score: int, bot_score: int, reason: str = None) -> str:
    """Response generation: concise per-round message (≤4 lines).

    Format:
    Round X
    User move / Bot move
    Result (+ reason if invalid)
    Updated score
    """
    # For any invalid outcome, present the standardized message required by spec
    if result == "Invalid":
        result_line = "Invalid – round wasted"
    else:
        result_line = result
    
    lines = [
        f"Round {round_number}",
        f"User move: {user_move} / Bot move: {bot_move}",
        f"Result: {result_line}",
        f"Score -> User: {user_score} | Bot: {bot_score}"
    ]
    return "\n".join(lines)


def final_result_message(user_score: int, bot_score: int) -> str:
    if user_score > bot_score:
        return "USER WINS"
    if bot_score > user_score:
        return "BOT WINS"
    return "DRAW"
# Note: file I/O and persistent state are intentionally removed from this
# module so it remains pure game logic. Persistent state must be mutated only
# via ADK tool contracts (see `adk_game_tools.py`).
