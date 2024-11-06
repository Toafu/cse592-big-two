from card import *
from player import *


def test_validate_singles():
    # TODO: Make deterministic
    Hand = [
        Card("Diamonds", "5"),
        Card("Clubs", "5"),
        Card("Spades", "8"),
        Card("Diamonds", "J"),
        Card("Hearts", "Q"),
    ]
    d = Deck()
    small_hand = d.cards[0:5]
    small_hand = sorted(small_hand)
    last_play = [Card("Hearts", "8")]

    split = bisect_right(small_hand, last_play[0])

    for i in range(split):
        assert small_hand[i] < last_play[0]

    for i in range(split, len(small_hand)):
        assert small_hand[i] > last_play[0]
