import json
import os
import tempfile
import unittest

from adk_agent import GameRefereeAgent


def load_state(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class GameRulesTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = os.path.join(self.tmpdir.name, "game_state.json")
        self.agent = GameRefereeAgent()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_bomb_first_time_allowed(self):
        resp = self.agent.play_round("bomb", self.state_path)
        state = load_state(self.state_path)

        self.assertIn("User wins", resp)
        self.assertTrue(state["user_used_bomb"])
        self.assertEqual(state["user_score"], 1)
        self.assertEqual(state["bot_score"], 0)
        self.assertEqual(state["round_number"], 1)

    def test_bomb_second_time_blocked(self):
        self.agent.play_round("bomb", self.state_path)
        resp = self.agent.play_round("bomb", self.state_path)
        state = load_state(self.state_path)

        self.assertIn("Invalid", resp)
        self.assertTrue(state["user_used_bomb"])
        self.assertEqual(state["user_score"], 1)  # first bomb win only
        self.assertEqual(state["bot_score"], 0)
        self.assertEqual(state["round_number"], 2)  # round increments on invalid

    def test_bomb_vs_bomb_draw(self):
        # advance rounds so bot uses bomb on round_number == 2
        self.agent.play_round("rock", self.state_path)  # round 1
        self.agent.play_round("rock", self.state_path)  # round 2
        resp = self.agent.play_round("bomb", self.state_path)  # round 3, bot bomb
        state = load_state(self.state_path)

        self.assertIn("Draw", resp)
        self.assertTrue(state["user_used_bomb"])
        self.assertTrue(state["bot_used_bomb"])
        self.assertEqual(state["round_number"], 3)

    def test_invalid_input_wastes_round(self):
        resp = self.agent.play_round("invalid_move", self.state_path)
        state = load_state(self.state_path)

        self.assertIn("Invalid", resp)
        self.assertEqual(state["user_score"], 0)
        self.assertEqual(state["bot_score"], 0)
        self.assertEqual(state["round_number"], 1)


if __name__ == "__main__":
    unittest.main()
