import random
import itertools
from enum import Enum
from collections import Counter
from functools import total_ordering
import typing


class Card:
    """
    Represent a card with a suit and rank.

    Can be compared to other Cards.
    """

    suits = {"Diamonds": 0, "Clubs": 1, "Hearts": 2, "Spades": 3}
    ranks = {
        "3": 0,
        "4": 1,
        "5": 2,
        "6": 3,
        "7": 4,
        "8": 5,
        "9": 6,
        "10": 7,
        "J": 8,
        "Q": 9,
        "K": 10,
        "A": 11,
        "2": 12,
    }

    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def __lt__(self, other: "Card"):
        return (self.rank_index(), self.suit_index()) < (
            other.rank_index(),
            other.suit_index(),
        )

    def __gt__(self, other: "Card"):
        return (self.rank_index(), self.suit_index()) > (
            other.rank_index(),
            other.suit_index(),
        )

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))

    def rank_index(self):
        return Card.ranks[self.rank]

    def suit_index(self):
        return Card.suits[self.suit]


@total_ordering
class CardCombination(Enum):
    """Represent a combination."""

    INVALID = -1
    ANY = 0
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    FULLHOUSE = 4
    STRAIGHT = 5
    FOUROFAKIND = 6

    def __str__(self) -> str:
        return self.name

    def __lt__(self, other: "CardCombination"):
        return self.value < other.value


Cards = typing.List[Card]


# to represent the type of combination
def __repr__(self):
    return self.name


def is_single(cards: Cards) -> bool:
    return len(cards) == 1


def is_pair(cards: Cards) -> bool:
    return len(cards) == 2 and cards[0].rank == cards[1].rank


def is_triple(cards: Cards) -> bool:
    return len(cards) == 3 and len(set(card.rank for card in cards)) == 1


def is_straight(cards: Cards) -> bool:
    if len(cards) != 5:
        return False
    sorted_cards = sorted(cards, key=lambda c: c.rank_index())
    for i in range(4):
        if (
            sorted_cards[i].rank_index() + 1
            != sorted_cards[i + 1].rank_index()
        ):
            return False
    return True


def is_full_house(cards: Cards) -> bool:
    rank_counts = Counter(card.rank for card in cards)
    return sorted(rank_counts.values()) == [2, 3]


def is_four_of_a_kind(cards: Cards) -> bool:
    rank_counts = Counter(card.rank for card in cards)
    return 4 in rank_counts.values() and len(cards) == 5


def is_valid_combination(cards: Cards) -> bool:
    return (
        is_single(cards)
        or is_pair(cards)
        or is_triple(cards)
        or is_straight(cards)
        or is_full_house(cards)
        or is_four_of_a_kind(cards)
    )


def identify_combination(cards: Cards) -> CardCombination:
    match len(cards):
        case 1:
            return CardCombination.SINGLE
        case 2:
            if is_pair(cards):
                return CardCombination.PAIR
        case 3:
            if is_triple(cards):
                return CardCombination.TRIPLE
        case 5:
            if is_four_of_a_kind(cards):
                return CardCombination.FOUROFAKIND
            if is_straight(cards):
                return CardCombination.STRAIGHT
            if is_full_house(cards):
                return CardCombination.FULLHOUSE
    return CardCombination.INVALID


class Play:
    """
    Represent a played combination.

    Standardizes the order of Cards.
    Can be compared with other Plays.
    """

    def __init__(
        self,
        cards: Cards = [],
        combination: CardCombination = CardCombination.ANY,
    ):
        """
        Initialize a Play object, standardizing the order of cards.
        The relevant portion of each hand is sorted.

        Put Cards that need to be compared at the back of the Play.
        Pairs and Straights: only compare just the best card.
        Full Houses and Four of a Kinds: compare ranks of triple or quad.
        """
        self.cards: Cards = cards
        self.combination: CardCombination = combination

        match self.combination:
            case CardCombination.PAIR | CardCombination.STRAIGHT:
                self.cards = sorted(self.cards)
            case CardCombination.FULLHOUSE | CardCombination.FOUROFAKIND:
                freq = Counter([c.rank for c in self.cards])
                # First sort the cards by frequency
                self.cards = sorted(self.cards, key=lambda x: freq[x.rank])
                # Then standardize each section
                if self.combination == CardCombination.FOUROFAKIND:
                    self.cards[1:] = sorted(self.cards[1:])
                else:
                    self.cards[0:2] = sorted(self.cards[0:2])
                    self.cards[2:] = sorted(self.cards[2:])
            case CardCombination.INVALID:
                assert False, "Combination must be valid"

    def __repr__(self):
        return f"{self.cards} → {self.combination}"

    def __lt__(self, other: "Play"):
        """Determine if self's Play < other's Play."""
        # All plays are better than ANY
        if (
            self.combination == CardCombination.ANY
            and other.combination != CardCombination.ANY
        ):
            return True
        elif (
            self.combination != CardCombination.ANY
            and other.combination == CardCombination.ANY
        ):
            return False
        # Four of a kinds beat all non four of a kinds
        if (
            self.combination != CardCombination.FOUROFAKIND
            and other.combination == CardCombination.FOUROFAKIND
        ):
            return True
        elif (
            self.combination == CardCombination.FOUROFAKIND
            and other.combination != CardCombination.FOUROFAKIND
        ):
            return False
        # At this point there are no more special rules
        if self.combination != other.combination:
            return False
        # Normal same combination compare
        return self.cards[-1] < other.cards[-1]

    def __eq__(self, other) -> bool:
        return (
            self.cards == other.cards and self.combination == other.combination
        )

    def __hash__(self) -> int:
        x = sum(hash(c) for c in self.cards)
        return x * self.combination.value


class Deck:
    """
    Represent a deck of Cards.

    Initializes already shuffled.
    """

    def __init__(self):
        self.cards = [
            Card(suit, rank)
            for suit, rank in itertools.product(Card.suits, Card.ranks)
        ]
        random.shuffle(self.cards)

    def deal(self, num_players):
        return [self.cards[i::num_players] for i in range(num_players)]
