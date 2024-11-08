from bisect import bisect_right
import itertools
import typing
from card import *


Cards = typing.List[Card]
Moves = typing.Tuple[Card, ...]


class Player:
    """The base player acts randomly."""

    def __init__(self, name, hand):
        self.name = name
        self.hand: Cards = sorted(hand)

    def find_plays(
        self,
        last_play: Play,
    ) -> list[Moves]:
        """
        Return all valid plays compatible with the current combination.

        Filter out all plays worse than last_play.
        """

        match last_play.combination:
            case CardCombination.SINGLE:
                return [
                    (self.hand[i],)  # Single element tuple
                    for i in range(
                        bisect_right(self.hand, last_play.cards[0]), len(self.hand)
                    )
                ]
            case CardCombination.PAIR:
                return self._find_same_rank_combos_(last_play, 2)
            case CardCombination.TRIPLE:
                return self._find_same_rank_combos_(last_play, 3)
            case CardCombination.FOUROFAKIND:
                freq = Counter([c.rank for c in self.hand])
                quad_ranks = [k for k, v in freq.items() if v == 4]
                return []

        # for combo_size in [1, 2, 3, 5]:  # Try different combination sizes
        #     possible_plays = itertools.combinations(self.hand, combo_size)
        # return possible_plays
        return []

    def _find_same_rank_combos_(self, last_play: Play, n: int) -> list[Moves]:
        assert (
            n == 2 or n == 3
        ), "This function only supports pairs and triples."
        plays: list[Moves] = []
        best_in_last_play: Card = max(last_play.cards)
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
    def find_plays(self, last_play: Play, current_combination=CardCombination.ANY):
        print(
            f"Your hand: {[f'{i}: {str(card)}' for i, card in enumerate(self.hand)]}"
        )
        print("Last play:", last_play if last_play else "None")
        # to print last play
        # if last_play:
        #     card_strings = [str(card) for card in last_play.cards]
        #     print("Last Play:", ", ".join(card_strings))
        #     lastplay = Play(last_play, current_combination)
        # else:
        #     print("Last Play: None")

        while True:
            play_input = input(
                "Enter indices of cards to play (e.g., '0 2 4' for a combination) or enter -1 to pass turn: "
            )
            try:
                indices = list(map(int, play_input.split()))
                selected_cards = [self.hand[i] for i in indices]

                # check for whether the player passed
                if len(indices) == 1 and indices[0] == -1:
                    return []

                # checking for whether the card that is played is of the current combination and whether is it valid combination and whether it is gre
                if is_valid_combination(selected_cards) and (
                    identify_combination(selected_cards) == current_combination
                ):
                    # check whether the selected cards are greater than the last play
                    # create a play here
                    selected_play = Play(selected_cards, current_combination)
                    # if last play is not None
                    if last_play.cards:
                        if last_play < selected_play:
                            for card in selected_cards:
                                self.hand.remove(card)
                            return [tuple(selected_cards)]
                    # if lastplay is none
                    else:
                        for card in selected_cards:
                            self.hand.remove(card)
                        return [tuple(selected_cards)]
                else:
                    print(
                        "Invalid combination or play not higher than last play."
                    )
            except (ValueError, IndexError):
                print("Invalid input. Try again.")


class AggressivePlayer(Player):
    pass
