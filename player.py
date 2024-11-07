from bisect import bisect_right
import itertools
import typing
from card import Card, CardCombination, is_valid_combination

Cards = typing.List[Card]
Moves = typing.Tuple[Card]


class Player:
    """The base player acts randomly."""

    def __init__(self, name, hand):
        self.name = name
        self.hand: Cards = sorted(hand)

    def find_plays(
        self,
        last_play: Cards = None,
        current_combination: CardCombination = CardCombination.ANY,
    ) -> list[Moves]:
        """
        Return all valid plays compatible with the current combination.

        Filter out all plays worse than last_play.
        """

        match current_combination:
            case CardCombination.SINGLE:
                return [
                    (self.hand[i],) # Single element tuple
                    for i in range(
                        bisect_right(self.hand, last_play[0]), len(self.hand)
                    )
                ]
            case CardCombination.PAIR:
                return self._find_same_rank_combos_(last_play, 2)
            case CardCombination.TRIPLE:
                return self._find_same_rank_combos_(last_play, 3)

        for combo_size in [1, 2, 3, 5]:  # Try different combination sizes
            possible_plays = itertools.combinations(self.hand, combo_size)
        return possible_plays

    def _find_same_rank_combos_(self, last_play, n: int) -> list[Moves]:
        assert n == 2 or n == 3, "This function only supports pairs and triples."
        plays: list[Cards] = []
        best_in_last_play: Card = max(last_play)
        i = bisect_right(self.hand, best_in_last_play)
        same_rank: list[Card] = []
        cur_rank = self.hand[i].rank
        while i < len(self.hand):
            if self.hand[i].rank == cur_rank:
                same_rank.append(self.hand[i])
                i += 1
            else:
                if len(same_rank) >= n:
                    combos = itertools.combinations(same_rank, n)
                    for c in combos:
                        plays.append(c)
                same_rank.clear()
                cur_rank = self.hand[i].rank
        return plays

    def has_cards(self):
        return len(self.hand) > 0


class HumanPlayer(Player):
    def find_plays(self, last_play=None):
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
