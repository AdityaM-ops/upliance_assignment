Google ADK integration (RPS-Plus)

- Uses the ADK surface `from google.adk import Agent, tool`.
- Tools are defined with `@tool` in `adk_game_tools.py`; agent invokes them via `Agent.invoke_tool`.
- Single mutation point: only `update_game_state` writes `game_state.json`.
- Runtime invocation log: `adk_runtime.log` is produced when the program runs.

Run:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python play_round.py
```
