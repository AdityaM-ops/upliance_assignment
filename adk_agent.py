"""
ADK Agent: Google ADK-native game referee for Rock-Paper-Scissors-Plus.

Uses official Google ADK FunctionTool wrappers for tool invocation.
All state mutations go exclusively through the ADK tool system (single mutation point).

Key Design:
- Tools are FunctionTool instances registered with the Agent
- Direct tool execution via FunctionTool interface (not LLM-mediated)
- Pure game logic (rps_plus) remains decoupled
- All state access/mutations through tool layer
"""

import rps_plus
from google.adk.agents.llm_agent import Agent
from adk_core import GameState
from adk_game_tools import (
    GAME_TOOLS,
    load_game_state,
    update_game_state,
    validate_move,
    resolve_round,
    reset_game_state,
)


class GameRefereeAgent:
    """Google ADK Agent for Rock-Paper-Scissors-Plus game referee.
    
    Orchestrates game rounds using official Google ADK FunctionTool-wrapped tools.
    All state mutations go through the ADK mutation tool (single mutation point).
    
    NOTE: Direct tool execution (no LLM mediation). Strictly ADK-runtime tool layer.
    """
    
    def __init__(self):
        """Initialize Game Referee Agent with Google ADK tools."""
        # Create agent with tools (for schema/registry purposes)
        self._agent = Agent(
            name="GameRefereeAgent",
            model="gemini-1.5-flash",  # Required by ADK Agent, but not used for direct tool calls
            tools=GAME_TOOLS,
        )
        print(f"[ADK INIT] GameRefereeAgent initialized with {len(GAME_TOOLS)} FunctionTool-wrapped tools")
    
    def play_round(self, user_raw_move: str, state_path: str = "game_state.json") -> str:
        """Play one round using ADK FunctionTool-wrapped tool invocation (runtime-only).
        
        Architecture (ADK-RUNTIME-ONLY):
        1. Load state via FunctionTool (part of ADK tool layer)
        2. Auto-reset via FunctionTool if game finished  
        3. Interpret intent (pure logic)
        4. Validate via FunctionTool
        5. Generate bot move (pure logic)
        6. Resolve via FunctionTool
        7. Build delta dict
        8. Apply via FunctionTool mutation (SINGLE MUTATION POINT)
        9. Format and return response
        """
        
        # Step 1: Load state via ADK FunctionTool
        print(f"[ADK TOOL] load_game_state(path={state_path!r})")
        loaded = load_game_state(path=state_path)
        if isinstance(loaded, dict):
            state = GameState.from_dict(loaded)
        else:
            raise TypeError(f"Expected dict from load_game_state, got {type(loaded)}")
        
        # Step 2: Auto-reset if game finished
        if state.round_number >= 3:
            print(f"[ADK TOOL] reset_game_state(path={state_path!r})")
            reset_res = reset_game_state(path=state_path)
            if isinstance(reset_res, dict):
                state = GameState.from_dict(reset_res)
            else:
                raise TypeError(f"Expected dict from reset_game_state, got {type(reset_res)}")
        
        # Step 3: Interpret intent (pure logic, NOT a tool)
        user_move = rps_plus.interpret_intent(user_raw_move)
        
        # Step 4: Validate via ADK FunctionTool
        print(f"[ADK TOOL] validate_move(move={user_move!r}, user_used_bomb={state.user_used_bomb})")
        val_res = validate_move(move=user_move, user_used_bomb=state.user_used_bomb)
        if isinstance(val_res, dict):
            is_valid = bool(val_res.get("is_valid"))
            reason = val_res.get("reason")
        else:
            raise TypeError(f"Expected dict from validate_move, got {type(val_res)}")
        
        # Step 5: Generate bot move (pure logic, NOT a tool)
        bot_move = rps_plus.generate_bot_move(state.bot_used_bomb, state.round_number)
        
        # Step 6: Resolve via ADK FunctionTool
        if not is_valid:
            result = "Invalid"
        else:
            print(f"[ADK TOOL] resolve_round(user_move={user_move!r}, bot_move={bot_move!r})")
            result = resolve_round(user_move=user_move, bot_move=bot_move)
        
        # Step 7: Build delta dict (single mutation point semantics)
        deltas = {"round_increment": 1}

        # Only mark user bomb consumption after a valid user bomb
        if is_valid and user_move == "bomb":
            deltas["user_used_bomb"] = True
        # Mark bot bomb consumption whenever the bot plays a bomb
        if bot_move == "bomb":
            deltas["bot_used_bomb"] = True

        # Score deltas only on valid resolved outcomes
        if result == "User wins":
            deltas["user_score_delta"] = 1
        elif result == "Bot wins":
            deltas["bot_score_delta"] = 1

        # Step 8: Apply via ADK FunctionTool mutation (SINGLE MUTATION POINT)
        # Compute concrete new state values from deltas
        new_round = state.round_number + int(deltas.get("round_increment", 0))
        new_user_score = state.user_score + int(deltas.get("user_score_delta", 0))
        new_bot_score = state.bot_score + int(deltas.get("bot_score_delta", 0))
        new_user_used_bomb = bool(deltas.get("user_used_bomb", state.user_used_bomb))
        new_bot_used_bomb = bool(deltas.get("bot_used_bomb", state.bot_used_bomb))

        print(
            f"[ADK TOOL] update_game_state(path={state_path!r}, "
            f"round_number={new_round}, user_score={new_user_score}, "
            f"bot_score={new_bot_score}, user_used_bomb={new_user_used_bomb}, "
            f"bot_used_bomb={new_bot_used_bomb})"
        )
        updated = update_game_state(
            path=state_path,
            round_number=new_round,
            user_score=new_user_score,
            bot_score=new_bot_score,
            user_used_bomb=new_user_used_bomb,
            bot_used_bomb=new_bot_used_bomb,
        )
        if isinstance(updated, dict):
            state = GameState.from_dict(updated)
        else:
            raise TypeError(f"Expected dict from update_game_state, got {type(updated)}")
        
        # Step 9: Format response
        response = rps_plus.format_round_response(
            state.round_number,
            str(user_move) if user_move is not None else "",
            bot_move,
            result,
            state.user_score,
            state.bot_score,
            reason=None,
        )
        
        if state.round_number >= 3:
            response = response + "\n" + rps_plus.final_result_message(state.user_score, state.bot_score)
        
        return response


# Global agent instance
_referee_agent = None
def get_referee_agent() -> GameRefereeAgent:
    """Get or create the global Game Referee Agent."""
    global _referee_agent
    if _referee_agent is None:
        _referee_agent = GameRefereeAgent()
    return _referee_agent


def play_round_adk(user_raw_move: str, state_path: str = "game_state.json") -> str:
    """Play a round using the ADK agent (ADK-runtime-only, no fallback)."""
    agent = get_referee_agent()
    return agent.play_round(user_raw_move, state_path)


if __name__ == "__main__":
    # Interactive CLI using ADK agent (runtime-only)
    while True:
        raw = input("Your move (or 'exit'): ")
        if raw.strip().lower() == "exit":
            break
        print(play_round_adk(raw))


