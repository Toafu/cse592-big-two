import random
import functools

from rlcard.utils import init_standard_deck
from rl_bigtwo.player import BigTwoPlayer as Player
from rl_bigtwo.utils import bigtwo_sort_card
from rlcard.games.doudizhu.utils import cards2str

class BigTwoDealer():
    """Deals cards to players."""
    def __init__(self):
        ''' Initialize a Blackjack dealer class
        '''
        self.deck = init_standard_deck()
        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck
        '''
        random.shuffle(self.deck)

    def deal_cards(self, players: list[Player]):
        ''' Deal cards to players

        Args:
            players (list): list of DoudizhuPlayer objects
        '''
        num_players = len(players)
        hands = [self.deck[i::num_players] for i in range(num_players)]
        for i, player in enumerate(players):
            current_hand = hands[i]
            current_hand.sort(key=functools.cmp_to_key(bigtwo_sort_card))
            player.set_hand(current_hand)
            player.initial_hand = cards2str(current_hand)