import numpy as np
from typing import Optional
import logging
import gymnasium as gym
from gymnasium import spaces
from card import (
    Color,
    CardCombination,
    Play,
    cards2box,
    box2cards,
    identify_combination,
)
from main import BigTwoGame
from player import *

LOGGER = logging.getLogger(__name__)

# 13766 with suits, 360 without
num_plays = 13766 + 1
num_cards = 52


class BigTwoEnv(gym.Env):
    def __init__(self, game: BigTwoGame) -> None:
        self.game = game
        self.num_agents: int = len(game.players)
        self.rl_agentid: int = next(i for i, p in enumerate(game.players) if isinstance(p, RLAgent))

        self.action_space: spaces.Space = spaces.Box(
            low=0, high=1, shape=(num_cards,), dtype=np.int8
        )
        self.observation_space = spaces.Tuple(
            (
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Box(
                    low=0, high=21, shape=(self.num_agents - 1,), dtype=np.int8
                ),
                spaces.Discrete(self.num_agents),
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
            np.asarray(opponent_hand_sizes, dtype=np.int8),
            self.game.last_player,
        )

    def _get_info(self):
        # TODO: Fix for round win
        return {"win_bonus": 5}

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[dict] = None
    ):
        """Players get new hands, discarded is empty, determine who starts."""
        super().reset(seed=seed)
        self.game.setup()
        return self._get_obs(), self._get_info()

    def step(self, action):
        assert self.action_space.contains(action)
        """
        Accepts an action

        Returns a tuple[observation (ObsType), reward (SupportsFloat), terminated (bool), truncated (bool), info (dict)]
        """
        current_player_index: int = self.game.current_player_index
        current_player = self.game.players[current_player_index]
        cards = box2cards(action)
        LOGGER.info("%s hand: %s", current_player.name, current_player.hand)
        play: Play = Play([], CardCombination.PASS)
        if cards:
            # Remove cards from that player's hand
            play = Play(cards, identify_combination(cards))
            LOGGER.info("Reconstructed play %r", play)
            for c in list(cards):
                current_player.hand.remove(c)

            # Set new last Play
            self.game.last_play = play

            # Set new last player
            self.game.last_player = current_player_index

            # Update passes
            self.game.passes[current_player_index] = False

            LOGGER.info("%s plays %s", current_player.name, play)
        else:
            # State doesn't change on PASS. Just update passes.
            self.game.passes[current_player_index] = True
            LOGGER.info("%s passes", current_player.name)

        self.game.round_agent_actions.append((current_player_index, play))

        # TODO: Tune this function
        # Give bonus for playing more cards
        reward = len(play.cards)

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
            LOGGER.info(
                "%sNew round%s",
                Color.BG_YELLOW_BRIGHT.value,
                Color.RESET.value,
            )

        return (
            self._get_obs(),
            reward,
            self.game.is_game_over(),
            False,
            self._get_info(),
        )
