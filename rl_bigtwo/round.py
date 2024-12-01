import numpy as np

class BigTwoRound:
    """Represent one Big Two round."""

    def __init__(self, np_random, played_cards):
        self.np_random = np_random
        self.played_cards = played_cards
        self.trace = [] # Records all actions in the game
