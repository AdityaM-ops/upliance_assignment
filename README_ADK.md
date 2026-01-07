Rock-Paper-Scissors-Plus (ADK-first Python referee)

Summary
- Deterministic, ADK-first referee for Rock-Paper-Scissors-Plus (best of 3).
- Valid moves: `rock`, `paper`, `scissors`, `bomb` (each player may use `bomb` once).
- Invalid input wastes the round (no score change) with reason shown (e.g., "bomb_already_used").

Strict Compliance
- **Game Semantics:** Invalid input increments round_number only; no score change; result = "Invalid – {reason}".
- **Bomb constraint:** Validation blocks re-used bomb BEFORE resolution.
- **Output:** Round responses ≤4 lines; contain Round X, Moves, Result, Score; final result after round 3.
- **ADK Layer:** Explicit Google ADK agent with schema registration, tool contracts, single mutation point.

Architecture
- `rps_plus.py`: Pure game logic (intent, resolution, response formatting).
- `adk_game_tools.py`: ADK GameState and SDK-decorated tool contracts (canonical tools module).
- `adk_agent.py`: ADK controller agent that calls tools exclusively via the Google ADK SDK executor.
- `play_round.py`: Thin wrapper for programmatic use.

ADK Tool Contract Schemas

GameState schema:
```json
{
  "name": "GameState",
  "properties": {
    "round_number": {"type": "integer"},
    "user_score": {"type": "integer"},
    "bot_score": {"type": "integer"},
    "user_used_bomb": {"type": "boolean"},
    "bot_used_bomb": {"type": "boolean"}
  }
}
```

update_game_state tool (mutation):
```json
{
  "name": "update_game_state",
  "input": {
    "state": "GameState",
    "deltas": {
      "round_increment": "int (optional)",
      "user_score_delta": "int (optional)",
      "bot_score_delta": "int (optional)",
      "user_used_bomb": "bool (optional)",
      "bot_used_bomb": "bool (optional)"
    },
    "path": "str (default: game_state.json)"
  },
  "output": "GameState"
}
```

validate_move_tool:
```json
{
  "name": "validate_move_tool",
  "input": {
    "move": "string | null",
    "used_bomb": "boolean"
  },
  "output": {
    "is_valid": "boolean",
    "reason": "string (e.g., 'invalid', 'bomb_already_used')"
  }
}
```

resolve_round_tool:
```json
{
  "name": "resolve_round_tool",
  "input": {
    "user_move": "string (rock|paper|scissors|bomb)",
    "bot_move": "string (rock|paper|scissors|bomb)"
  },
  "output": "string (User wins | Bot wins | Draw | Invalid)"
}
```

ADK Agent Invocation Example

```python
from adk_agent import play_round_adk
from adk_game_tools import GameState

# Direct agent invocation using SDK-backed tool calls:
response = play_round_adk('rock')
print(response)

# Schemas are declared in `adk_game_tools.py` via the Google ADK decorators.

# Example output (Round 1):
# Round 1
# User move: rock / Bot move: bomb
# Result: Bot wins
# Score -> User: 0 | Bot: 1

# Example with invalid move (bomb re-use):
# Round 2
# User move: bomb / Bot move: rock
# Result: Invalid – bomb_already_used
# Score -> User: 0 | Bot: 1
```

Design Rationale
- **Single mutation point:** All state changes via `invoke_update_tool` or `invoke_reset_tool` ensures auditability.
- **Schema-first:** Explicit tool schemas (JSON) emulate real ADK contract registration.
- **Agent class:** RockPaperScissorsPlusAgent demonstrates proper ADK orchestration.
- **No external APIs:** Bot randomness from Python `random.choice` only.

Violations Fixed
✓ Invalid input no longer transfers points; shows reason (e.g., "bomb_already_used").
✓ Bomb validation blocks re-use before resolution.
✓ Round responses ≤4 lines with Round #, Moves, Result, Score.
✓ Explicit Google ADK agent class with schema registration.
✓ Tool contract schemas documented in code.
✓ ADK invocation example in README.

Run locally

```powershell
cd "C:\Users\Asus\Desktop\assignment"
python play_round.py
```

Programmatic usage

```python
from play_round import play_round
print(play_round('rock'))
```

Files
`rps_plus.py`, `adk_game_tools.py`, `adk_agent.py`, `play_round.py`, `game_state.json`, `README.md`, `README_ADK.md`

