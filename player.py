from bisect import bisect, bisect_left, bisect_right
from collections import deque
import itertools
import typing
from card import *


Cards = typing.List[Card]
Moves = typing.Tuple[Card, ...]


class Player:
    """The base player acts randomly."""

    def __init__(self, name, hand):
        self.name: str = name
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
            # TODO: Integrate FOUROFAKIND into all of these
            # TODO: Integrate ANY
            case CardCombination.SINGLE:
                return [
                    (self.hand[i],)  # Single element tuple
                    for i in range(
                        bisect_right(self.hand, last_play.cards[0]),
                        len(self.hand),
                    )
                ]
            case CardCombination.PAIR:
                return self._find_same_rank_combos_(last_play, 2)
            case CardCombination.TRIPLE:
                return self._find_same_rank_combos_(last_play, 3)
            case CardCombination.FOUROFAKIND:
                return self._find_four_of_a_kinds_(last_play)
            case CardCombination.FULLHOUSE:
                # Only the triple matters, so any pair should be allowed
                pairs = self._find_same_rank_combos_(
                    Play(
                        [],
                        CardCombination.PAIR,
                    ),
                    2,
                )
                triples = self._find_same_rank_combos_(
                    Play(last_play.cards[2:], CardCombination.TRIPLE), 3
                )
                return [
                    *(
                        (p + t)
                        for p in pairs
                        for t in triples
                        if p[0].rank != t[0].rank
                    )
                ]
            case CardCombination.STRAIGHT:
                # Cursed dynamic sliding window
                moves: list[Moves] = []
                best_card_in_play = max(last_play.cards)
                least_viable_rank = list(Card.ranks)[
                    best_card_in_play.rank_index() - 4
                ]
                i = bisect_left(
                    self.hand, Card("Diamonds", str(least_viable_rank))
                )
                straight_buffer: deque[Card] = deque()
                straight_buffer.append(self.hand[i])
                i += 1
                while i < len(self.hand):
                    if (
                        self.hand[i].rank_index()
                        - straight_buffer[0].rank_index()
                        >= 5
                        and straight_buffer[-1].rank_index()
                        - straight_buffer[0].rank_index()
                        == 4
                    ):
                        possible_moves = self._get_straight_combinations_(
                            list(straight_buffer)
                        )
                        for m in possible_moves:
                            if last_play < Play(
                                list(m), CardCombination.STRAIGHT
                            ):
                                moves.append(m)
                        # Remove all instances of the first rank in the deque
                        rank_to_remove: str = straight_buffer[0].rank
                        while straight_buffer[0].rank == rank_to_remove:
                            straight_buffer.popleft()
                    else:
                        # Append to deque if rank is same or +1
                        if (
                            self.hand[i].rank_index()
                            - straight_buffer[-1].rank_index()
                            <= 1
                        ):
                            straight_buffer.append(self.hand[i])
                        else:
                            straight_buffer.clear()
                            straight_buffer.append(self.hand[i])
                        i += 1
                return moves
        return []

    def _find_same_rank_combos_(self, last_play: Play, n: int) -> list[Moves]:
        assert (
            n == 2 or n == 3
        ), "This function only supports pairs and triples."
        moves: list[Moves] = []
        i = (
            bisect_right(self.hand, max(last_play.cards))
            if len(last_play.cards)
            else 0
        )
        same_rank: list[Card] = []
        cur_rank = self.hand[i].rank
        while i <= len(self.hand):
            if i != len(self.hand) and self.hand[i].rank == cur_rank:
                same_rank.append(self.hand[i])
                i += 1
            else:
                if len(same_rank) >= n:
                    combos = itertools.combinations(same_rank, n)
                    for c in combos:
                        moves.append(c)
                if i == len(self.hand):
                    break
                same_rank.clear()
                cur_rank = self.hand[i].rank
        return moves

    def _find_four_of_a_kinds_(self, last_play: Play) -> list[Moves]:
        moves: list[Moves] = []
        freq = Counter([c.rank for c in self.hand])
        quad_ranks = [k for k, v in freq.items() if v == 4]
        for q_rank in quad_ranks:
            q_idx = bisect_left(self.hand, Card("Diamonds", q_rank))
            quad = self.hand[q_idx : q_idx + 4]
            i: int = 0
            while i < len(self.hand):
                if i == q_idx:
                    i += 4
                    continue
                moves.append(tuple(quad + [self.hand[i]]))
                i += 1
        return moves

    def _get_straight_combinations_(self, cards: Cards) -> list[Moves]:
        def backtrack(path: Cards, remaining: Cards):
            if len(path) == 5:
                results.append(tuple(path))
                return
            if not remaining:
                return
            for i, card in enumerate(remaining):
                rank = card.rank
                if rank not in selected_ranks:
                    selected_ranks.add(rank)
                    backtrack(path + [card], remaining[i + 1 :])
                    selected_ranks.remove(rank)

        results: list[Moves] = []
        selected_ranks: set[str] = set()
        backtrack([], cards)
        return results

    def has_cards(self):
        return len(self.hand) > 0


class HumanPlayer(Player):
    def find_plays(
        self, last_play: Play, current_combination=CardCombination.ANY
    ):
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
