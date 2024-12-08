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
        self.rl_agentid: int = next(
            i for i, p in enumerate(game.players) if isinstance(p, RLAgent)
        )

        # "Key cards" * combinations + pass
        self.action_space: spaces.Space = spaces.Discrete((num_cards * 6) + 1)
        self.observation_space = spaces.Tuple(
            (
                spaces.Discrete((num_cards * 6) + 1 + 1),  # + any
                spaces.Box(low=0, high=1, shape=(num_cards,), dtype=np.int8),
                spaces.Discrete(self.num_agents),
            )
        )

        """
        observation = {
            "last_play": 2                      # Last (greatest) play
            "player_hand": [1, 0, 1, ..., 0]    # Cards in the player's hand
        }
        """

    def _get_obs(self):
        return (
            play2discrete(self.game.last_play),
            cards2box(self.game.players[self.rl_agentid].hand),
            self.game.last_player,
        )

    def _get_info(self):
        # TODO: Fix for round win
        return {"win_bonus": 5}

    def _new_round(self):
        """Resets last play and passes."""
        # Reset last play
        self.game.last_play = Play()
        # Reset passes
        self.game.passes = [False] * self.num_agents
        LOGGER.info(
            "%sNew round%s",
            Color.BG_YELLOW_BRIGHT.value,
            Color.RESET.value,
        )

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[dict] = None
    ):
        """Players get new hands, discarded is empty, determine who starts."""
        super().reset(seed=seed)
        self.game.setup()
        while self.game.current_player_index != self.rl_agentid:
            self.game.play_turn()
            self.game.next_player()
        return self._get_obs(), self._get_info()

    def step(self, action):
        assert self.action_space.contains(action)
        """
        Accepts an action

        Returns a tuple[observation (ObsType), reward (SupportsFloat), terminated (bool), truncated (bool), info (dict)]
        """

        # TODO: Tune this function
        # Give bonus for RLAgent playing more cards

        current_player_index: int = self.game.current_player_index
        current_player = self.game.players[current_player_index]
        assert isinstance(current_player, RLAgent)
        LOGGER.info("%s hand: %s", current_player.name, current_player.hand)

        play: Play = current_player.make_play(
            current_player.find_plays(
                self.game.last_play, self.game.turns == 0
            ),
            self._get_obs(),
        )
        reward: int = len(play.cards)
        if play.combination != CardCombination.PASS:
            # Remove cards from that player's hand
            for c in play.cards:
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

        # Increments turn count
        self.game.turns += 1

        # Check for game end

        if self.game.is_game_over():
            if current_player_index == self.rl_agentid:
                reward += 100
            # TODO: Consider how to implement loss
        else:
            i = 1
            while not self.game.is_game_over() and i < self.num_agents:
                self.game.next_player()
                if self.game.check_other_passes():
                    self._new_round()
                self.game.play_turn()
                # Increments turn count
                self.game.turns += 1
                # Set new current player
                i += 1

            if not self.game.is_game_over():
                # Set new current player
                self.game.next_player()

                # Check for round end
                if self.game.check_other_passes():
                    self._new_round()
                    reward += 20

        return (
            self._get_obs(),
            reward,
            self.game.is_game_over(),
            False,
            self._get_info(),
        )
