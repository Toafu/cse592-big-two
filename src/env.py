import numpy as np
from typing import Optional
import gymnasium as gym
from gymnasium import spaces
from card import cards2box
from main import *

# 13766 with suits, 360 without
num_plays = 13766 + 1
num_cards = 52


class BigTwoEnv(gym.Env):
    def __init__(self, num_agents: int = 2, rl_agentid: int = 0) -> None:
        self.num_agents: int = num_agents
        self.rl_agentid: int = rl_agentid

        self.action_space = spaces.Discrete(num_plays)

        self.observation_space = spaces.Dict(
            {
                "last_play": spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                "hand": spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                "discarded": spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                "opponent_hand_sizes": spaces.Box(
                    low=0, high=21, shape=(num_agents - 1,), dtype=np.int32
                ),
                "last_player": spaces.Discrete(num_agents)
            }
        )

        """
        observation = {
            "last_play": [0, 1, 0, ..., 1]      # Last (greatest) play
            "player_hand": [1, 0, 1, ..., 0]    # Cards in the player's hand
            "discarded": [0, 0, 0, ..., 1],     # Cards on the table
            "opponent_hand_size": [10, 5, 3]    # Cards left for opponents
            "recent_player": 1                  # Last (grestest) playerID
        }
        """

        self.reset()

    def _get_obs(self):
        opponent_hand_sizes = [
            len(p.hand)
            for i, p in enumerate(self.game.players)
            if i != self.rl_agentid
        ]
        return (
            cards2box(self.game.last_play.cards),
            cards2box(self.game.players[self.rl_agentid].hand),
            [],
            opponent_hand_sizes,
            self.game.current_player_index,
        )

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[dict] = None
    ):
        """Players get new hands, discarded is empty, determine who starts."""
        super().reset(seed=seed)
        self.game = BigTwoGame(
            self.num_agents, [PlayerType.RLAgent, PlayerType.Random]
        )
        return self._get_obs(), {}

    def step(self, action):
        """
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        direction = self._action_to_direction[action]
        # We use `np.clip` to make sure we don't leave the grid bounds
        self._agent_location = np.clip(
            self._agent_location + direction, 0, self.size - 1
        )

        # An environment is completed if and only if the agent has reached the target
        terminated = np.array_equal(self._agent_location, self._target_location)
        truncated = False
        reward = 1 if terminated else 0  # the agent is only reached at the end of the episode
        observation = self._get_obs()
        info = self._get_info()
        """

        reward = 0
        # TODO: FIX EVERYTHING DOWN HERE
        return self._get_obs(), reward, False, self.game.is_game_over(), {}
