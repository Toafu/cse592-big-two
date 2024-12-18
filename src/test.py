from card import *
from player import *
from env import *


def test_compare_pairs():
    PAIR = CardCombination.PAIR
    diamond_spades = Play([Card("Diamonds", "5"), Card("Spades", "5")], PAIR)
    clubs_hearts = Play([Card("Clubs", "5"), Card("Hearts", "5")], PAIR)
    assert clubs_hearts < diamond_spades

    kings = Play([Card("Diamonds", "K"), Card("Spades", "K")], PAIR)
    fives = Play([Card("Clubs", "5"), Card("Hearts", "5")], PAIR)
    assert fives == fives
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


def test_compare_cardcombinations():
    assert CardCombination.SINGLE < CardCombination.TRIPLE
    assert CardCombination.PAIR == CardCombination.PAIR


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
    ctx = p.find_plays(last_play)

    split = bisect_right(p.hand, last_play.cards[0])
    unavailable_plays = [[i] for i in p.hand[0:split]]

    for play in ctx.available_plays:
        assert last_play < play

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
    ctx = p.find_plays(last_play)
    all_ctx = p.find_plays(Play([], combo))
    unavailable_plays = set(all_ctx.available_plays) - set(ctx.available_plays)
    for play in ctx.available_plays:
        assert last_play < play
    for play in unavailable_plays:
        assert play < last_play


def test_validate_pairs_none():
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
    last_play = Play([Card("Spades", "2"), Card("Clubs", "2")], combo)
    ctx = p.find_plays(last_play)
    assert len(ctx.available_plays) == 0


def test_validate_fourofakinds_normal():
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
    p = Player("Quaddington", hand)
    combo = CardCombination.FOUROFAKIND
    last_play = Play(
        [
            Card("Spades", "6"),
            Card("Clubs", "6"),
            Card("Hearts", "6"),
            Card("Diamonds", "6"),
            Card("Spades", "2"),
        ],
        CardCombination.FOUROFAKIND,
    )
    available_plays = set(p.find_plays(last_play).available_plays)
    validation_set_sevens: set[Play] = set(
        Play(fourofakind_seven + [e], CardCombination.FOUROFAKIND)
        for e in everything_else_seven
    )
    validation_set = validation_set_sevens
    assert available_plays == validation_set


def test_validate_fourofakinds_special():
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
    last_play = Play(
        [Card("Spades", "A"), Card("Clubs", "A")], CardCombination.PAIR
    )
    available_plays = set(p.find_plays(last_play).available_plays)
    validation_set_sevens: set[Play] = set(
        Play(fourofakind_seven + [e], CardCombination.FOUROFAKIND)
        for e in everything_else_seven
    )
    validation_set_fives: set[Play] = set(
        Play(fourofakind_five + [e], CardCombination.FOUROFAKIND)
        for e in everything_else_five
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
    available_plays = set(p.find_plays(last_play).available_plays)
    all_pairs = p._find_same_rank_combos_(
        Play(),
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
    combo = CardCombination.STRAIGHT
    available_plays = set(p.find_plays(last_play).available_plays)
    validation_list: list[Play] = [
        Play(
            [
                Card("Spades", "6"),
                Card("Diamonds", "7"),
                Card("Diamonds", "8"),
                Card("Spades", "9"),
                Card("Spades", "10"),
            ],
            combo,
        ),
        Play(
            [
                Card("Spades", "6"),
                Card("Spades", "7"),
                Card("Diamonds", "8"),
                Card("Spades", "9"),
                Card("Spades", "10"),
            ],
            combo,
        ),
        Play(
            [
                Card("Diamonds", "7"),
                Card("Diamonds", "8"),
                Card("Spades", "9"),
                Card("Clubs", "10"),
                Card("Diamonds", "J"),
            ],
            combo,
        ),
        Play(
            [
                Card("Diamonds", "7"),
                Card("Diamonds", "8"),
                Card("Spades", "9"),
                Card("Spades", "10"),
                Card("Diamonds", "J"),
            ],
            combo,
        ),
        Play(
            [
                Card("Spades", "7"),
                Card("Diamonds", "8"),
                Card("Spades", "9"),
                Card("Clubs", "10"),
                Card("Diamonds", "J"),
            ],
            combo,
        ),
        Play(
            [
                Card("Spades", "7"),
                Card("Diamonds", "8"),
                Card("Spades", "9"),
                Card("Spades", "10"),
                Card("Diamonds", "J"),
            ],
            combo,
        ),
    ]
    validation_set = set(validation_list)
    assert available_plays == validation_set

    p.hand = [
        Card("Spades", "J"),
        Card("Spades", "Q"),
        Card("Diamonds", "K"),
        Card("Spades", "A"),
        Card("Spades", "2"),
        Card("Diamonds", "2"),
        Card("Clubs", "2"),
    ]

    assert len(p.find_plays(last_play).available_plays) == 3


def test_validate_straights_special():
    hand: list[Card] = [
        Card("Diamonds", "3"),
        Card("Diamonds", "4"),
        Card("Diamonds", "5"),
        Card("Diamonds", "6"),
    ]

    p = Player("p", hand)
    assert (
        len(p.find_plays(Play([], CardCombination.STRAIGHT)).available_plays)
        == 0
    )

    hand: list[Card] = [
        Card("Diamonds", "3"),
        Card("Diamonds", "3"),
        Card("Diamonds", "5"),
        Card("Diamonds", "6"),
        Card("Diamonds", "7"),
        Card("Diamonds", "8"),
    ]

    small_straight: Play = Play(
        [
            Card("Clubs", "3"),
            Card("Clubs", "4"),
            Card("Clubs", "5"),
            Card("Clubs", "6"),
            Card("Clubs", "7"),
        ],
        CardCombination.STRAIGHT,
    )

    p.hand = hand
    assert len(p.find_plays(small_straight).available_plays) == 0

    p.hand = [
        Card("Spades", "A"),
        Card("Clubs", "2"),
        Card("Diamonds", "2"),
        Card("Hearts", "2"),
        Card("Spades", "2"),
    ]
    assert len(p.find_plays(small_straight).available_plays) == 1

    p.hand = [
        Card("Hearts", "3"),
        Card("Spades", "3"),
        Card("Hearts", "5"),
        Card("Spades", "5"),
        Card("Spades", "8"),
        Card("Clubs", "9"),
        Card("Spades", "9"),
    ]

    last_play = Play(
        [
            Card("Hearts", "10"),
            Card("Clubs", "J"),
            Card("Diamonds", "Q"),
            Card("Spades", "K"),
            Card("Hearts", "A"),
        ],
        CardCombination.STRAIGHT,
    )

    assert len(p.find_plays(last_play).available_plays) == 0


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


def test_start_game():
    hand = [
        Card("Clubs", "3"),
        Card("Hearts", "3"),
        Card("Diamonds", "3"),
        Card("Spades", "3"),
        Card("Clubs", "4"),
        Card("Diamonds", "5"),
        Card("Clubs", "5"),
        Card("Clubs", "J"),
        Card("Spades", "J"),
        Card("Hearts", "J"),
        Card("Clubs", "Q"),
        Card("Spades", "A"),
        Card("Spades", "2"),
    ]
    """
    13 singles = 13
    6 pairs of threes + 1 pair of fives + 3 pairs jacks = 10
    4 triples of threes and 1 triple of jacks = 5
    9 four of a kinds with threes = 9
    0 straights = 0
    16 full houses with triple threes + 7 full houses with triple jacks = 23
    """
    num_plays = 13 + 10 + 5 + 9 + 23
    p = Player("Toafu", hand)
    # Since quads can be played "any time", we cannot overcount them
    # Subtract 9 from all play counts (except quad) to not double count them
    assert (
        len(p.find_plays(Play([], CardCombination.SINGLE)).available_plays) - 9
        == 13
    )
    assert (
        len(p.find_plays(Play([], CardCombination.PAIR)).available_plays) - 9
        == 10
    )
    assert (
        len(p.find_plays(Play([], CardCombination.TRIPLE)).available_plays) - 9
        == 5
    )
    assert (
        len(
            p.find_plays(Play([], CardCombination.FOUROFAKIND)).available_plays
        )
        == 9
    )
    assert (
        len(p.find_plays(Play([], CardCombination.STRAIGHT)).available_plays)
        - 9
        == 0
    )
    assert (
        len(p.find_plays(Play([], CardCombination.FULLHOUSE)).available_plays)
        - 9
        == 23
    )
    assert len(p.find_plays(Play()).available_plays) == num_plays


def test_play_fourofakind_on_single():
    hand = [
        Card("Clubs", "3"),
        Card("Hearts", "3"),
        Card("Diamonds", "3"),
        Card("Spades", "3"),
        Card("Clubs", "7"),
        Card("Diamonds", "10"),
        Card("Clubs", "K"),
    ]

    last_play = Play([Card("Spades", "9")], CardCombination.SINGLE)
    p = Player("", hand)
    validation_set: set[Play] = set()
    for quad in p.find_plays(
        Play([], CardCombination.FOUROFAKIND)
    ).available_plays:
        validation_set.add(quad)
    validation_set.add(Play([Card("Diamonds", "10")], CardCombination.SINGLE))
    validation_set.add(Play([Card("Clubs", "K")], CardCombination.SINGLE))
    available_plays = set(p.find_plays(last_play).available_plays)
    for play in p.find_plays(last_play).available_plays:
        assert play in validation_set
    for play in validation_set:
        assert play in available_plays


def test_invalid_combos():
    single_ten = Play([Card("Spades", "10")], CardCombination.SINGLE)
    pair_twos = Play(
        [Card("Spades", "2"), Card("Diamonds", "2")], CardCombination.PAIR
    )
    straight_six_ten = Play(
        [
            Card("Hearts", "6"),
            Card("Hearts", "7"),
            Card("Hearts", "8"),
            Card("Hearts", "9"),
            Card("Hearts", "10"),
        ],
        CardCombination.STRAIGHT,
    )
    assert not single_ten < pair_twos
    assert not pair_twos < single_ten
    assert not straight_six_ten < single_ten
    assert not single_ten < straight_six_ten


def test_make_play():
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

    p = Player("Rando", hand)
    chosen_play = p.make_play(p.find_plays())
    for c in chosen_play.cards:
        assert c in p.hand


def test_aggressive_player():
    hand = [
        Card("Clubs", "3"),
        Card("Hearts", "3"),
        Card("Diamonds", "3"),
        Card("Spades", "3"),
        Card("Clubs", "4"),
        Card("Diamonds", "5"),
        Card("Clubs", "5"),
        Card("Clubs", "J"),
        Card("Spades", "J"),
        Card("Hearts", "J"),
        Card("Clubs", "Q"),
        Card("Spades", "A"),
        Card("Spades", "2"),
    ]

    p = AggressivePlayer("Aggro", hand)
    chosen_play = p.make_play(p.find_plays())
    assert chosen_play == Play(
        [
            Card("Clubs", "3"),
            Card("Hearts", "3"),
            Card("Diamonds", "3"),
            Card("Spades", "3"),
            Card("Spades", "2"),
        ],
        CardCombination.FOUROFAKIND,
    )
    for card in chosen_play.cards:
        assert card in p.hand


def test_playitsafe_player():
    hand = [
        Card("Diamonds", "3"),
        Card("Hearts", "3"),
        Card("Spades", "3"),
        Card("Clubs", "4"),
        Card("Diamonds", "5"),
        Card("Clubs", "5"),
        Card("Clubs", "J"),
        Card("Spades", "J"),
        Card("Hearts", "J"),
        Card("Clubs", "Q"),
        Card("Spades", "6"),
        Card("Spades", "7"),
    ]

    p = PlayItSafePlayer("Safety", hand)
    ctx = p.find_plays(game_start=True)
    chosen_play = p.make_play(ctx)
    start_play = Play(
        [
            Card("Diamonds", "3"),
            Card("Hearts", "3"),
            Card("Spades", "3"),
            Card("Diamonds", "5"),
            Card("Clubs", "5"),
        ],
        CardCombination.FULLHOUSE,
    )

    assert chosen_play == start_play

    p = PlayItSafePlayer("Safety", hand)
    last_play = Play([Card("Spades", "3")], CardCombination.SINGLE)
    chosen_play = p.make_play(p.find_plays(last_play))
    assert chosen_play == Play([Card("Clubs", "4")], CardCombination.SINGLE)

    hand = [
        Card("Clubs", "3"),
        Card("Hearts", "3"),
        Card("Spades", "3"),
        Card("Clubs", "4"),
        Card("Diamonds", "A"),
        Card("Clubs", "A"),
        Card("Clubs", "J"),
        Card("Spades", "J"),
        Card("Hearts", "J"),
        Card("Clubs", "Q"),
        Card("Spades", "6"),
        Card("Spades", "7"),
    ]

    p = PlayItSafePlayer("Safety", hand)
    chosen_play = p.make_play(p.find_plays())
    assert chosen_play == Play(
        [Card("Clubs", "3"), Card("Hearts", "3"), Card("Spades", "3")],
        CardCombination.TRIPLE,
    )

    hand = [
        Card("Clubs", "3"),
        Card("Hearts", "4"),
        Card("Spades", "5"),
        Card("Clubs", "6"),
        Card("Diamonds", "7"),
        Card("Clubs", "A"),
        Card("Clubs", "J"),
        Card("Spades", "J"),
        Card("Hearts", "J"),
        Card("Clubs", "Q"),
        Card("Spades", "6"),
        Card("Spades", "7"),
    ]

    p = PlayItSafePlayer("Safety", hand)
    chosen_play = p.make_play(p.find_plays())
    assert chosen_play == Play(
        [
            Card("Clubs", "3"),
            Card("Hearts", "4"),
            Card("Spades", "5"),
            Card("Clubs", "6"),
            Card("Diamonds", "7"),
        ],
        CardCombination.STRAIGHT,
    )
    hand = [
        Card("Clubs", "3"),
        Card("Hearts", "4"),
        Card("Spades", "5"),
        Card("Clubs", "6"),
        Card("Diamonds", "7"),
        Card("Clubs", "A"),
        Card("Clubs", "J"),
        Card("Spades", "J"),
        Card("Hearts", "J"),
        Card("Clubs", "Q"),
        Card("Spades", "3"),
        Card("Spades", "7"),
    ]

    p = PlayItSafePlayer("Safety", hand)
    chosen_play = p.make_play(p.find_plays())
    assert chosen_play == Play(
        [Card("Clubs", "3"), Card("Spades", "3")], CardCombination.PAIR
    )


def test_no_options():
    """make_play should not be called when forced to pass."""
    hand = [Card("Clubs", "J")]

    p = Player("Almost", hand)
    last_play = Play([Card("Spades", "K")], CardCombination.SINGLE)
    assert len(p.find_plays(last_play).available_plays) == 0


def test_small_hand():
    hand = [Card("Clubs", "8")]

    p = Player("", hand)

    last_play: Play = Play([Card("Clubs", "9")], CardCombination.SINGLE)
    assert len(p.find_plays(last_play).available_plays) == 0

    last_play: Play = Play(
        [Card("Clubs", "9"), Card("Hearts", "9")], CardCombination.PAIR
    )
    assert len(p.find_plays(last_play).available_plays) == 0

    last_play: Play = Play(
        [Card("Clubs", "9"), Card("Hearts", "9"), Card("Spades", "9")],
        CardCombination.TRIPLE,
    )
    assert len(p.find_plays(last_play).available_plays) == 0

    last_play: Play = Play(
        [
            Card("Clubs", "9"),
            Card("Hearts", "9"),
            Card("Spades", "10"),
            Card("Clubs", "10"),
            Card("Hearts", "10"),
        ],
        CardCombination.FULLHOUSE,
    )
    assert len(p.find_plays(last_play).available_plays) == 0

    last_play: Play = Play(
        [
            Card("Clubs", "5"),
            Card("Hearts", "6"),
            Card("Hearts", "7"),
            Card("Hearts", "8"),
            Card("Hearts", "9"),
        ],
        CardCombination.STRAIGHT,
    )
    assert len(p.find_plays(last_play).available_plays) == 0

    last_play: Play = Play(
        [
            Card("Clubs", "9"),
            Card("Hearts", "9"),
            Card("Spades", "9"),
            Card("Diamonds", "9"),
            Card("Clubs", "3"),
        ],
        CardCombination.FOUROFAKIND,
    )
    assert len(p.find_plays(last_play).available_plays) == 0


def test_simplify_play():
    p: Play = Play(
        [
            Card("Clubs", "3"),
            Card("Hearts", "3"),
            Card("Hearts", "10"),
            Card("Hearts", "3"),
            Card("Hearts", "10"),
        ],
        CardCombination.FULLHOUSE,
    )

    assert p.simplify_play() == "TT333"

    p = Play(
        [
            Card("Clubs", "3"),
            Card("Hearts", "7"),
            Card("Hearts", "6"),
            Card("Hearts", "4"),
            Card("Hearts", "5"),
        ],
        CardCombination.STRAIGHT,
    )

    assert p.simplify_play() == "34567"


def test_cards2box():
    cards = [
        Card("Clubs", "3"),
        Card("Hearts", "7"),
        Card("Hearts", "6"),
        Card("Hearts", "4"),
        Card("Hearts", "5"),
    ]

    b = cards2box(cards)
    card_indexes = set([c.card_index() for c in cards])
    for i in range(52):
        if i in card_indexes:
            assert b[i] == 1
        else:
            assert b[i] == 0


def test_box2cards():
    box = [0] * 52
    box[5] = 1  # 4 of Clubs
    box[40] = 1  # King of Diamonds
    box[37] = 1  # Queen of Clubs
    box[9] = 1  # 5 of Clubs
    box[19] = 1  # 7 of Spades

    validation_cards: Cards = [
        Card("Clubs", "4"),
        Card("Clubs", "5"),
        Card("Spades", "7"),
        Card("Clubs", "Q"),
        Card("Diamonds", "K"),
    ]

    assert box2cards(box) == validation_cards


def test_env():
    e = BigTwoEnv()
    obs = e._get_obs()
    last_play, player_hand, discarded, opponent_hand_size, last_player = obs
    assert sum(last_play) == 0
    assert sum(discarded) == 0
    print(e.game.players)
    assert sum(player_hand) == opponent_hand_size[0]
    assert last_player == 0
