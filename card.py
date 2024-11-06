import random
import itertools
from enum import Enum
from collections import Counter

class CardCombination(Enum):
	ANY = -1
	SINGLE = 0
	PAIR = 1
	TRIPLE = 2
	FULLHOUSE = 3
	STRAIGHT = 4
	FOUROFAKIND = 5

# Combination Identification Functions
def is_single(cards: list):
    return len(cards) == 1

def is_pair(cards):
    return len(cards) == 2 and cards[0].rank == cards[1].rank

def is_triple(cards):
    return len(cards) == 3 and len(set(card.rank for card in cards)) == 1

def is_straight(cards):
    if len(cards) != 5:
        return False
    sorted_cards = sorted(cards, key=lambda c: c.rank_index())
    for i in range(4):
        if sorted_cards[i].rank_index() + 1 != sorted_cards[i + 1].rank_index():
            return False
    return True

def is_full_house(cards):
    rank_counts = Counter(card.rank for card in cards)
    return sorted(rank_counts.values()) == [2, 3]

def is_four_of_a_kind(cards):
    rank_counts = Counter(card.rank for card in cards)
    return 4 in rank_counts.values() and len(cards) == 5

def is_valid_combination(cards):
    return (is_single(cards) or is_pair(cards) or is_triple(cards) or 
            is_straight(cards) or is_full_house(cards) or 
            is_four_of_a_kind(cards))

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

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def __lt__(self, other):
        return (self.rank_index(), self.suit_index()) < (
            other.rank_index(),
            other.suit_index(),
        )
    def __gt__(self, other):
        return (self.rank_index(), self.suit_index()) > (
            other.rank_index(),
            other.suit_index(),
        )

    def rank_index(self):
        return Card.ranks[self.rank]

    def suit_index(self):
        return Card.suits[self.suit]


class Deck:
    def __init__(self):
        self.cards = [
            Card(suit, rank)
            for suit, rank in itertools.product(Card.suits, Card.ranks)
        ]
        random.shuffle(self.cards)

    def deal(self, num_players):
        return [self.cards[i::num_players] for i in range(num_players)]
