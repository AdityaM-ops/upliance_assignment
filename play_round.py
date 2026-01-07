from adk_agent import play_round_adk


def play_round(user_raw_move: str) -> str:
    """Wrapper that invokes the ADK controller agent to play a round.

    This function is the recommended entrypoint for programmatic callers and
    demonstrates the ADK-first flow: controller (agent) calls tool(s) to mutate state.
    """
    return play_round_adk(user_raw_move)


if __name__ == "__main__":
    while True:
        raw = input("Your move (or 'exit'): ")
        if raw.strip().lower() == "exit":
            break
        print(play_round(raw))
