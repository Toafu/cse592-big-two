from card import *
from player import *


def test_compare_pairs():
    diamond_spades: Play = Play(
        [Card("Diamonds", "5"), Card("Spades", "5")], CardCombination.PAIR
    )
    clubs_hearts: Play = Play(
        [Card("Clubs", "5"), Card("Hearts", "5")], CardCombination.PAIR
    )
    assert clubs_hearts < diamond_spades

    kings: Play = Play(
        [Card("Diamonds", "K"), Card("Spades", "K")], CardCombination.PAIR
    )
    fives: Play = Play(
        [Card("Clubs", "5"), Card("Hearts", "5")], CardCombination.PAIR
    )
    assert fives < kings


def test_validate_singles():
    hand = [
        Card("Diamonds", "J"),
        Card("Diamonds", "5"),
        Card("Spades", "8"),
        Card("Clubs", "5"),
        Card("Hearts", "Q"),
    ]

    p = Player("Singleton", hand)
    last_play: Cards = [Card("Hearts", "8")]
    combo = CardCombination.SINGLE
    available_plays = p.find_play(last_play, combo)

    split = bisect_right(p.hand, last_play[0])
    unavailable_plays = [[i] for i in p.hand[0:split]]

    for cards in available_plays:
        assert Play(last_play, combo) < Play(cards, combo)

    for cards in unavailable_plays:
        assert Play(cards, combo) < Play(last_play, combo)
