Rock-Paper-Scissors-Plus (Python, Google ADK)

- Best of 3; moves: rock, paper, scissors, bomb (one bomb per player).
- Invalid input wastes the round (round increments, no score change).
- Only the ADK mutation tool `update_game_state` writes `game_state.json`.

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
