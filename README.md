Rock-Paper-Scissors-Plus (Python)

Rules (brief):
- Best of 3 rounds; game ends automatically after 3 rounds.
- Valid moves: rock, paper, scissors, bomb.
- Each player may use `bomb` only once per game; `bomb` beats rock/paper/scissors.
- `bomb` vs `bomb` is a draw. Invalid inputs waste the round and count toward 3 rounds.

Files:
- `rps_plus.py`: core logic (intent interpretation, validation, resolution, response generation).
- `play_round.py`: simple runner exposing `play_round(user_move)`.
- `game_state.json`: persistent state file used by the runner.

Run locally:

```bash
python play_round.py
```

Or import `play_round.play_round` and call with a string move to get the concise per-round response.
