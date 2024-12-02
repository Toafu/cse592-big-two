import numpy as np

from player import BigTwoPlayer as Player


class BigTwoGame:
    def __init__(self, num_players=2, allow_step_back=False) -> None:
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = num_players

    def init_game(self):
        self.winner_id = None
        self.history = []

        self.players: list[Player] = [
            Player(i, self.np_random) for i in range(self.num_players)
        ]
