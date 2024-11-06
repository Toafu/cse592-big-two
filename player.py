import random
from bisect import bisect_right
import itertools
import typing
from collections import Counter
from card import Card, CardCombination, is_valid_combination

Play = typing.List[Card]


class Player:
    def __init__(self, name, hand):
        self.name = name
        self.hand = sorted(hand)

    def find_play(
        self,
        last_play: Play = None,
        current_combination: CardCombination = CardCombination.ANY,
    ):
        """
        Return all valid plays compatible with the current combination.

        Filter out all plays worse than last_play.
        """
        match current_combination:
            case CardCombination.SINGLE:
                return self.hand[bisect_right(self.hand, last_play[0]) : :]
            case CardCombination.PAIR:
                a: list = []
                cur_number = self.hand[0]
                c: Card
                for c in self.hand:
                    pass

        for combo_size in [1, 2, 3, 5]:  # Try different combination sizes
            possible_plays = itertools.combinations(self.hand, combo_size)
        return possible_plays

    def has_cards(self):
        return len(self.hand) > 0


# Human Player Class
class HumanPlayer(Player):
    def find_play(self, last_play=None):
        print(f"Your hand: {[str(card) for card in self.hand]}")
        print("Last play:", last_play if last_play else "None")

        while True:
            play_input = input(
                "Enter indices of cards to play (e.g., '0 2 4' for a combination): "
            )
            try:
                indices = list(map(int, play_input.split()))
                selected_cards = [self.hand[i] for i in indices]

                if is_valid_combination(selected_cards) and (
                    not last_play or selected_cards > last_play
                ):
                    for card in selected_cards:
                        self.hand.remove(card)
                    return selected_cards
                else:
                    print(
                        "Invalid combination or play not higher than last play."
                    )
            except (ValueError, IndexError):
                print("Invalid input. Try again.")


class AggressivePlayer(Player):
    pass
