import random
import itertools
from enum import Enum
from collections import Counter
import typing


class Card:
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

    def rank_index(self):
        return Card.ranks[self.rank]

    def suit_index(self):
        return Card.suits[self.suit]


class CardCombination(Enum):
    INVALID = -999
    ANY = -1
    SINGLE = 0
    PAIR = 1
    TRIPLE = 2
    FULLHOUSE = 3
    STRAIGHT = 4
    FOUROFAKIND = 5


Cards = typing.List[Card]


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
    """Represent a played combination. Easy to compare."""

    def __init__(self, cards: Cards, combination: CardCombination):
        """Initialize a Play object, standardizing the order of cards."""
        self.cards: Cards = cards
        self.combination: CardCombination = combination

        match self.combination:
            # Prioritize the tiebreaker case at the end
            # Singles and Triples don't require reordering
            case CardCombination.PAIR | CardCombination.STRAIGHT:
                self.cards = sorted(self.cards)
            # Put the more frequent ranks at the back
            # Full House [Double, Triple]
            # Four of a Kind [Single, Quadruple]
            case CardCombination.FULLHOUSE | CardCombination.FOUROFAKIND:
                freq = Counter([c.rank for c in self.cards])
                self.cards = sorted(self.cards, key=lambda x: freq[x.rank])
            case CardCombination.ANY:
                assert False, "Combination cannot be declared as ANY"

    def __lt__(self, other: "Play"):
        return self.cards[-1] < other.cards[-1]


class Deck:
    def __init__(self):
        self.cards = [
            Card(suit, rank)
            for suit, rank in itertools.product(Card.suits, Card.ranks)
        ]
        random.shuffle(self.cards)

    def deal(self, num_players):
        return [self.cards[i::num_players] for i in range(num_players)]
