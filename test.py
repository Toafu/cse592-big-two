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

    pair = [
        Card("Diamonds", "8"),
        Card("Spades", "8"),
    ]

    assert Play(pair, CardCombination.PAIR) < Play(
        fourofakind_high, FOUROFAKIND
    )

    assert not Play(fourofakind_high, FOUROFAKIND) < Play(
        pair, CardCombination.PAIR
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
    combo = CardCombination.SINGLE
    last_play: Play = Play([Card("Hearts", "8")], combo)
    available_plays = p.find_plays(last_play)

    split = bisect_right(p.hand, last_play.cards[0])
    unavailable_plays = [[i] for i in p.hand[0:split]]

    for moves in available_plays:
        assert last_play < Play(list(moves), combo)

    for cards in unavailable_plays:
        assert Play(cards, combo) < last_play


def test_validate_pairs():
    hand = [
        Card("Spades", "7"),
        Card("Hearts", "5"),
        Card("Hearts", "7"),
        Card("Spades", "3"),
        Card("Clubs", "Q"),
        Card("Diamonds", "5"),
        Card("Hearts", "3"),
        Card("Diamonds", "J"),
        Card("Diamonds", "6"),
        Card("Spades", "J"),
        Card("Spades", "9"),
        Card("Diamonds", "Q"),
        Card("Clubs", "7"),
    ]
    p = Player("Pairington", hand)
    combo = CardCombination.PAIR
    last_play = Play([Card("Spades", "5"), Card("Clubs", "5")], combo)
    available_plays = p.find_plays(last_play)
    all_plays = p.find_plays(
        Play([Card("Clubs", "3"), Card("Diamonds", "3")], combo)
    )
    unavailable_plays = set(all_plays) - set(available_plays)
    for move in available_plays:
        assert last_play < Play(list(move), combo)
    for move in unavailable_plays:
        assert Play(list(move), combo) < last_play


def test_validate_fourofakinds():
    hand = [
        Card("Spades", "3"),
        Card("Hearts", "3"),
        Card("Diamonds", "3"),
        Card("Clubs", "3"),
        Card("Spades", "5"),
        Card("Spades", "A"),
    ]

    assert not is_four_of_a_kind(hand)

    hand = [
        Card("Spades", "7"),
        Card("Hearts", "5"),
        Card("Hearts", "7"),
        Card("Clubs", "5"),
        Card("Hearts", "3"),
        Card("Diamonds", "7"),
        Card("Diamonds", "6"),
        Card("Spades", "J"),
        Card("Spades", "9"),
        Card("Diamonds", "Q"),
        Card("Clubs", "7"),
        Card("Diamonds", "5"),
        Card("Spades", "5"),
    ]
    fourofakind_seven = [
        Card("Diamonds", "7"),
        Card("Clubs", "7"),
        Card("Hearts", "7"),
        Card("Spades", "7"),
    ]
    fourofakind_five = [
        Card("Diamonds", "5"),
        Card("Clubs", "5"),
        Card("Hearts", "5"),
        Card("Spades", "5"),
    ]
    everything_else_seven = [
        Card("Spades", "5"),
        Card("Hearts", "3"),
        Card("Clubs", "5"),
        Card("Diamonds", "6"),
        Card("Hearts", "5"),
        Card("Spades", "J"),
        Card("Spades", "9"),
        Card("Diamonds", "5"),
        Card("Diamonds", "Q"),
    ]
    everything_else_five = [
        Card("Spades", "7"),
        Card("Hearts", "3"),
        Card("Clubs", "7"),
        Card("Diamonds", "6"),
        Card("Hearts", "7"),
        Card("Spades", "J"),
        Card("Spades", "9"),
        Card("Diamonds", "7"),
        Card("Diamonds", "Q"),
    ]
    p = Player("Quaddington", hand)
    combo = CardCombination.FOUROFAKIND
    last_play = Play([Card("Spades", "5"), Card("Clubs", "5")], combo)
    available_plays = set(p.find_plays(last_play))
    validation_set_sevens = set(
        tuple(fourofakind_seven + [e]) for e in everything_else_seven
    )
    validation_set_fives = set(
        tuple(fourofakind_five + [e]) for e in everything_else_five
    )
    validation_set = validation_set_fives | validation_set_sevens
    assert available_plays == validation_set


def test_validate_full_houses():
    hand = [
        Card("Spades", "7"),
        Card("Hearts", "7"),
        Card("Hearts", "3"),
        Card("Hearts", "9"),
        Card("Spades", "Q"),
        Card("Diamonds", "7"),
        Card("Spades", "J"),
        Card("Clubs", "9"),
        Card("Diamonds", "Q"),
        Card("Diamonds", "3"),
        Card("Clubs", "3"),
        Card("Spades", "9"),
        Card("Diamonds", "5"),
    ]
    p = Player("Full Housington", hand)
    combo = CardCombination.FULLHOUSE
    last_play = Play(
        [
            Card("Spades", "5"),
            Card("Clubs", "5"),
            Card("Hearts", "5"),
            Card("Spades", "2"),
            Card("Diamonds", "2"),
        ],
        combo,
    )
    available_plays = set(p.find_plays(last_play))
    all_pairs = p._find_same_rank_combos_(
        Play(
            [],
            CardCombination.PAIR,
        ),
        2,
    )
    triples = [
        (Card("Diamonds", "7"), Card("Hearts", "7"), Card("Spades", "7")),
        (Card("Clubs", "9"), Card("Hearts", "9"), Card("Spades", "9")),
    ]
    pairs_with_sevens = [
        (Card("Diamonds", "3"), Card("Clubs", "3")),
        (Card("Diamonds", "3"), Card("Hearts", "3")),
        (Card("Clubs", "3"), Card("Diamonds", "3")),
        (Card("Clubs", "9"), Card("Hearts", "9")),
        (Card("Clubs", "9"), Card("Spades", "9")),
        (Card("Hearts", "9"), Card("Spades", "9")),
        (Card("Diamonds", "Q"), Card("Spades", "Q")),
    ]
    full_houses_with_seven = []
    for p in pairs_with_sevens:
        full_houses_with_seven.append(p + triples[0])
    assert len(full_houses_with_seven) == 7
    for f in full_houses_with_seven:
        assert (
            is_full_house(list(f))
            and Play(list(f), CardCombination.FULLHOUSE) > last_play
        )
    assert len(all_pairs) == 10
    for p in available_plays:
        print(p)
    assert len(available_plays) == 14


def test_validate_straights():
    hand = [
        Card("Spades", "3"),
        Card("Hearts", "4"),
        Card("Spades", "6"),
        Card("Diamonds", "7"),
        Card("Spades", "7"),
        Card("Diamonds", "8"),
        Card("Spades", "9"),
        Card("Clubs", "10"),
        Card("Spades", "10"),
        Card("Diamonds", "3"),
        Card("Diamonds", "J"),
        Card("Clubs", "2"),
        Card("Spades", "A"),
    ]

    last_play = Play(
        [
            Card("Hearts", "6"),
            Card("Hearts", "7"),
            Card("Hearts", "8"),
            Card("Hearts", "9"),
            Card("Hearts", "10"),
        ],
        CardCombination.STRAIGHT,
    )

    p = Player("Straightington", hand)
    available_plays = set(p.find_plays(last_play))
    validation_list: list[Moves] = [
        (
            Card("Spades", "6"),
            Card("Diamonds", "7"),
            Card("Diamonds", "8"),
            Card("Spades", "9"),
            Card("Spades", "10"),
        ),
        (
            Card("Spades", "6"),
            Card("Spades", "7"),
            Card("Diamonds", "8"),
            Card("Spades", "9"),
            Card("Spades", "10"),
        ),
        (
            Card("Diamonds", "7"),
            Card("Diamonds", "8"),
            Card("Spades", "9"),
            Card("Clubs", "10"),
            Card("Diamonds", "J"),
        ),
        (
            Card("Diamonds", "7"),
            Card("Diamonds", "8"),
            Card("Spades", "9"),
            Card("Spades", "10"),
            Card("Diamonds", "J"),
        ),
        (
            Card("Spades", "7"),
            Card("Diamonds", "8"),
            Card("Spades", "9"),
            Card("Clubs", "10"),
            Card("Diamonds", "J"),
        ),
        (
            Card("Spades", "7"),
            Card("Diamonds", "8"),
            Card("Spades", "9"),
            Card("Spades", "10"),
            Card("Diamonds", "J"),
        ),
    ]
    validation_set = set(validation_list)
    assert available_plays == validation_set


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
