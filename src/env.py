import numpy as np
from typing import Optional
import gymnasium as gym
from gymnasium import spaces
from card import Play, cards2box, box2cards, identify_combination
from main import BigTwoGame, PlayerType
# 13766 with suits, 360 without
num_plays = 13766 + 1
num_cards = 52


class BigTwoEnv(gym.Env):
    def __init__(self, num_agents: int = 2, rl_agentid: int = 0) -> None:
        self.num_agents: int = num_agents
        self.rl_agentid: int = rl_agentid

        self.action_space: spaces.Space = spaces.Box(
            low=0, high=1, shape=(num_cards,), dtype=np.int8
        )
        self.observation_space = spaces.Tuple(
            (
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Box(
                    low=0, high=21, shape=(num_agents - 1,), dtype=np.int32
                ),
                spaces.Discrete(num_agents),
            )
        )

        """
        observation = {
            "last_play": [0, 1, 0, ..., 1]      # Last (greatest) play
            "player_hand": [1, 0, 1, ..., 0]    # Cards in the player's hand
            "discarded": [0, 0, 0, ..., 1],     # Cards on the table
            "opponent_hand_size": [10, 5, 3]    # Cards left for opponents
            "last_player": 1                    # Last (grestest) playerID
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
            cards2box(self.game.discarded),
            opponent_hand_sizes,
            self.game.last_player,
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
        assert self.action_space.contains(action)
        """
        Accepts an action

        Returns a tuple[observation (ObsType), reward (SupportsFloat), terminated (bool), truncated (bool), info (dict)]
        """
        current_player_index: int = self.game.current_player_index
        current_player = self.game.players[current_player_index]
        cards = box2cards(action)
        if cards:
            # Remove cards from that player's hand
            play = Play(cards, identify_combination(cards))
            # TODO: REMOVE THIS LOGIC FROM PLAYERS
            for c in cards:
                current_player.hand.remove(c)
            
            # Set new last Play
            self.game.last_play = play

            # Set new last player
            self.game.last_player = current_player_index

            # Update passes
            self.game.passes[current_player_index] = False
        
        else:
            self.game.passes[current_player_index] = True
        
        # TODO: Calculate reward
        # Give bonus for playing more cards
        # You can detect if a round has started if last_play == Play()
        reward = 0
        
        # Increments turn count
        self.game.turns += 1

        # Set new current player
        self.game.next_player()

        # If a round is over
        if self.game.check_other_passes():
            # Reset last_play
            self.game.last_play = Play()

            # Reset passes
            self.game.passes = [False] * self.num_agents

        return self._get_obs(), reward, False, self.game.is_game_over(), {}
