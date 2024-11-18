from rlcard.utils import init_standard_deck
import numpy as np

class BigTwoDealer():
    """Deals cards to players."""
    def __init__(self, np_random):
        ''' Initialize a Blackjack dealer class
        '''
        self.np_random = np_random
        self.deck = init_standard_deck()
        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, players):
        ''' Deal cards to players

        Args:
            players (list): list of DoudizhuPlayer objects
        '''
