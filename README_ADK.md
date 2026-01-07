Rock-Paper-Scissors-Plus (Google ADK)

- Uses the ADK surface `from google.adk import Agent, tool`.
- ADK tools are defined in `adk_game_tools.py`; only `update_game_state` writes `game_state.json`.
- Agent calls tools exclusively through `Agent.invoke_tool`, with invocation logs in `adk_runtime.log`.
- Game rules: best of 3, one bomb per player, invalid move wastes the round (round increments, no score delta).

Run:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python play_round.py
```

