Google ADK integration (RPS-Plus)

This project was migrated to use the official Google ADK SDK as the primary
agent/controller. All tools are declared using the Google ADK decorator and
schemas. The project expects the `google_adk` package to be installed.

Install

```bash
pip install -r requirements.txt
```

Tool schemas (declared via Google ADK decorator)

- load_game_state
  - input: { path: string }
  - output: GameState schema

- validate_move
  - input: { move: string|null, user_used_bomb: boolean }
  - output: { is_valid: boolean, reason: string }

- resolve_round
  - input: { user_move: string, bot_move: string }
  - output: string enum ["User wins","Bot wins","Draw","Invalid"]

- update_game_state
  - input: { state: object, deltas: object }
  - output: GameState schema

- reset_game_state
  - input: { path: string }
  - output: GameState schema

Run log (example)

This is a short sample of what a successful run using the Google ADK SDK might
produce once the SDK is installed and the `invoke_tool` API is present.

- Tool registration (SDK output)
  - register tool: load_game_state
  - register tool: validate_move
  - register tool: resolve_round
  - register tool: update_game_state
  - register tool: reset_game_state

- Example session (3 rounds):

Round 1
User move: rock / Bot move: rock
Result: Draw
Score -> User: 0 | Bot: 0

Round 2
User move: paper / Bot move: paper
Result: Draw
Score -> User: 0 | Bot: 0

Round 3
User move: bomb / Bot move: bomb
Result: Draw
Score -> User: 0 | Bot: 0

Final: DRAW

Notes

- The project enforces a SINGLE MUTATION POINT: `update_game_state` is the only
  function that writes `game_state.json`.
- Invalid inputs increment the round only and return the standardized message
  `Invalid – round wasted` (no score deltas).
- The bot move generation is deterministic to make behavior reproducible.

If your installed Google ADK SDK exposes different function names than
`invoke_tool` or `gadk.tool`, adapt `adk_agent.py` and `adk_game_tools.py` to
match the SDK API surface.
