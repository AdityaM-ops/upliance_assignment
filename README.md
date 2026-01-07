Rock-Paper-Scissors-Plus (Python, Google ADK)

- Best of 3; moves: rock, paper, scissors, bomb (one bomb per player).
- Invalid input wastes the round (round increments, no score change).
- Only the ADK mutation tool `update_game_state` writes `game_state.json`.

STATE MODEL
Core state is a single GameState type defined in `adk_core.py`.  
Persistent representation uses deterministic JSON fields: round_number, user_score, bot_score, user_used_bomb, bot_used_bomb.  
State transitions occur once per round through `update_game_state` after resolution deltas are produced by the agent.

AGENT AND TOOL DESIGN
ADK tools are declared in `adk_game_tools.py` using `@tool` from `google.adk`.  
The orchestrator `adk_agent.py` manages the match lifecycle and invokes every capability exclusively via `Agent.invoke_tool("tool_name", kwargs)`.  
Validation tool `validate_move` enforces bomb-once contract using parameter `user_used_bomb`.  
Execution registry `_TOOL_REGISTRY` performs lookup so that logic modules remain isolated and I/O is confined to ADK surfaces.

TRADEOFFS
Bot move generation relies on deterministic tables in `rps_plus.py` rather than external APIs to guarantee reproducible grading.  
Single mutation point simplifies audit and eliminates concurrent-write defects.  
Removal of local shim files ensures dependence only on the actual Google ADK package available in the runtime environment.

IMPROVEMENTS WITH MORE TIME
Add comparative adaptive strategy while preserving side-effect free core logic.  
Increase unit tests for null and second-bomb scenarios.  
Provide debugging visualization without introducing non-ADK mutation paths.

Files:
- `rps_plus.py`: pure game logic (intent, validation, resolution, formatting).
- `adk_game_tools.py`: ADK tools declared with `@tool` from `google.adk`.
- `adk_agent.py`: orchestrates rounds via `Agent.invoke_tool` (ADK runtime only).
- `play_round.py`: CLI/programmatic entry; uses ADK agent.


Run locally:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python play_round.py
```
