from card import *
from player import *


def test_compare_pairs():
    PAIR = CardCombination.PAIR
    diamond_spades = Play([Card("Diamonds", "5"), Card("Spades", "5")], PAIR)
    clubs_hearts = Play([Card("Clubs", "5"), Card("Hearts", "5")], PAIR)
    assert clubs_hearts < diamond_spades

    kings = Play([Card("Diamonds", "K"), Card("Spades", "K")], PAIR)
    fives = Play([Card("Clubs", "5"), Card("Hearts", "5")], PAIR)
    assert fives < kings


def test_compare_triples():
    TRIPLE = CardCombination.TRIPLE
    aces = Play(
        [Card("Hearts", "A"), Card("Diamonds", "A"), Card("Clubs", "A")],
        TRIPLE,
    )
    fours = Play(
        [Card("Hearts", "4"), Card("Spades", "4"), Card("Clubs", "4")], TRIPLE
    )

    assert fours < aces


def test_compare_fullhouses():
    FULLHOUSE = CardCombination.FULLHOUSE

    # [A, A, 4, 4, 4]
    fullhouse_low = [
        Card("Clubs", "A"),
        Card("Spades", "4"),
        Card("Clubs", "4"),
        Card("Hearts", "4"),
        Card("Diamonds", "A"),
    ]

    # [3, 3, 5, 5, 5]
    fullhouse_high = [
        Card("Clubs", "3"),
        Card("Spades", "5"),
        Card("Diamonds", "3"),
        Card("Clubs", "5"),
        Card("Hearts", "5"),
    ]

    assert Play(fullhouse_low, FULLHOUSE) < Play(fullhouse_high, FULLHOUSE)


def test_compare_fourofakinds():
    FOUROFAKIND = CardCombination.FOUROFAKIND

    # [2, 4, 4, 4, 4]
    fourofakind_low = [
        Card("Clubs", "4"),
        Card("Diamonds", "4"),
        Card("Hearts", "4"),
        Card("Spades", "2"),
        Card("Spades", "4"),
    ]

    # [3, 6, 6, 6, 6]
    fourofakind_high = [
        Card("Hearts", "6"),
        Card("Spades", "3"),
        Card("Clubs", "6"),
        Card("Diamonds", "6"),
        Card("Spades", "6"),
    ]

    assert Play(fourofakind_low, FOUROFAKIND) < Play(
        fourofakind_high, FOUROFAKIND
    )


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
    available_plays = p.find_plays(last_play, combo)

    split = bisect_right(p.hand, last_play[0])
    unavailable_plays = [[i] for i in p.hand[0:split]]

    for cards in available_plays:
        assert Play(last_play, combo) < Play(cards, combo)

    for cards in unavailable_plays:
        assert Play(cards, combo) < Play(last_play, combo)


def test_construct_plays():
    pair = [Card("Hearts", "2"), Card("Clubs", "2")]
    assert is_pair(pair)
    assert Play(pair, CardCombination.PAIR).cards[-1].suit == "Hearts"

    fullhouse = [
        Card("Clubs", "7"),
        Card("Spades", "4"),
        Card("Diamonds", "7"),
        Card("Clubs", "4"),
        Card("Hearts", "4"),
    ]
    assert is_full_house(fullhouse)

    fullhouse_play = Play(fullhouse, CardCombination.FULLHOUSE)
    for i in range(2):
        assert fullhouse_play.cards[i].rank == "7"
    for i in range(2, len(fullhouse)):
        assert fullhouse_play.cards[i].rank == "4"

    fourofakind = [
        Card("Clubs", "7"),
        Card("Hearts", "4"),
        Card("Diamonds", "7"),
        Card("Hearts", "7"),
        Card("Spades", "7"),
    ]
    assert is_four_of_a_kind(fourofakind)

    fourofakind_play = Play(fourofakind, CardCombination.FOUROFAKIND)
    assert fourofakind_play.cards[0].rank == "4"
    for i in range(1, len(fourofakind)):
        assert fourofakind_play.cards[i].rank == "7"


def test_identify_combinations():
    hand = [Card("Diamonds", "2")]
    assert identify_combination(hand) == CardCombination.SINGLE

    hand = [Card("Diamonds", "2"), Card("Clubs", "7")]
    assert identify_combination(hand) == CardCombination.INVALID

    hand = []
    assert identify_combination(hand) == CardCombination.INVALID

    hand = [Card("Diamonds", "2"), Card("Clubs", "2")]
    assert identify_combination(hand) == CardCombination.PAIR

    # Straights must be consecutive increasing rank priority
    hand = [
        Card("Diamonds", "2"),
        Card("Diamonds", "3"),
        Card("Diamonds", "4"),
        Card("Diamonds", "5"),
        Card("Diamonds", "6"),
    ]
    assert identify_combination(hand) == CardCombination.INVALID

    hand = [
        Card("Diamonds", "J"),
        Card("Diamonds", "Q"),
        Card("Diamonds", "K"),
        Card("Clubs", "A"),
        Card("Diamonds", "2"),
    ]
    assert identify_combination(hand) == CardCombination.STRAIGHT
