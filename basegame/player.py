from bisect import bisect_left, bisect_right
from collections import deque
import itertools
import typing
import random
from card import *


Cards = typing.List[Card]


class Player:
    """The base player acts randomly."""

    def __init__(self, name, hand):
        self.name: str = name
        self.hand: Cards = sorted(hand)

    def find_plays(
        self,
        last_play: Play,
    ) -> list[Play]:
        """
        Return all valid plays compatible with the current combination.

        Filter out all plays worse than last_play.
        """
        assert last_play.combination != CardCombination.INVALID
        if last_play.combination == CardCombination.ANY:
            assert len(last_play.cards) == 0
        all_combos: list[CardCombination] = [
            CardCombination.SINGLE,
            CardCombination.PAIR,
            CardCombination.TRIPLE,
            CardCombination.FULLHOUSE,
            CardCombination.STRAIGHT,
            CardCombination.FOUROFAKIND,
        ]
        search_combinations: list[CardCombination] = [last_play.combination]
        match last_play.combination:
            case CardCombination.ANY:
                search_combinations = all_combos
            case CardCombination.FOUROFAKIND:
                pass  # Do nothing extra
            case _:
                search_combinations.append(CardCombination.FOUROFAKIND)

        moves: list[Play] = []
        for c in search_combinations:
            match c:
                case CardCombination.SINGLE:
                    begin_bound = self._find_first_viable_rank_(last_play)
                    if begin_bound == -1:
                        continue
                    moves += [
                        Play([self.hand[i]], c)
                        for i in range(
                            begin_bound,
                            len(self.hand),
                        )
                    ]
                case CardCombination.PAIR:
                    moves += self._find_same_rank_combos_(last_play, 2)
                case CardCombination.TRIPLE:
                    moves += self._find_same_rank_combos_(last_play, 3)
                case CardCombination.FULLHOUSE:
                    # Only the triple matters, so any pair should be allowed
                    pairs = self._find_same_rank_combos_(Play(), 2)
                    triples = self._find_same_rank_combos_(
                        Play(last_play.cards[2:], CardCombination.TRIPLE), 3
                    )
                    moves += [
                        Play(p.cards + t.cards, c)
                        for p in pairs
                        for t in triples
                        if p.cards[0].rank != t.cards[0].rank
                    ]
                case CardCombination.STRAIGHT:
                    # Cursed dynamic sliding window
                    if len(self.hand) < 5:
                        continue
                    i = (
                        bisect_left(
                            self.hand,
                            Card(
                                "Diamonds",
                                str(
                                    list(Card.ranks)[
                                        max(last_play.cards).rank_index() - 4
                                    ]
                                ),
                            ),
                        )
                        if len(last_play.cards)
                        else 0
                    )
                    if i == len(self.hand):
                        continue
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
                            possible_plays = self._get_straight_combinations_(
                                list(straight_buffer)
                            )
                            for p in possible_plays:
                                if last_play < p:
                                    moves.append(p)
                            # Remove all instances of the first rank in deque
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
                case CardCombination.FOUROFAKIND:
                    moves += self._find_four_of_a_kinds_(last_play)
        return moves

    def _find_first_viable_rank_(self, last_play: Play) -> int:
        """
        Return index of first valid card to be considered.

        Returns 0 if all cards are viable.
        Returns -1 if no cards are viable.
        """
        if len(last_play.cards):
            i = bisect_right(self.hand, max(last_play.cards))
            if i == len(self.hand):
                return -1
            return i
        else:
            return 0

    def _find_same_rank_combos_(self, last_play: Play, n: int) -> list[Play]:
        assert (
            n == 2 or n == 3
        ), "This function only supports pairs and triples."
        combination = (
            CardCombination.PAIR if n == 2 else CardCombination.TRIPLE
        )
        moves: list[Play] = []
        i = self._find_first_viable_rank_(last_play)
        if i == -1:
            return []
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
                        moves.append(Play(list(c), combination))
                if i == len(self.hand):
                    break
                same_rank.clear()
                cur_rank = self.hand[i].rank
        return moves

    def _find_four_of_a_kinds_(self, last_play: Play) -> list[Play]:
        moves: list[Play] = []
        freq = Counter([c.rank for c in self.hand])
        quad_ranks = [k for k, v in freq.items() if v == 4]
        least_viable_rank_index: int = (
            last_play.cards[-1].rank_index()
            if (
                len(last_play.cards)
                and last_play.combination == CardCombination.FOUROFAKIND
            )
            else -1
        )
        for q_rank in quad_ranks:
            # Skip quads with lower ranks than last_play
            if Card.ranks[q_rank] < least_viable_rank_index:
                continue
            q_idx = bisect_left(self.hand, Card("Diamonds", q_rank))
            quad = self.hand[q_idx : q_idx + 4]
            i: int = 0
            while i < len(self.hand):
                if i == q_idx:
                    i += 4
                    continue
                moves.append(
                    Play(quad + [self.hand[i]], CardCombination.FOUROFAKIND)
                )
                i += 1
        return moves

    def _get_straight_combinations_(self, cards: Cards) -> list[Play]:
        def backtrack(hand: Cards, remaining: Cards):
            if len(hand) == 5:
                results.append(Play(hand, CardCombination.STRAIGHT))
                return
            if not remaining:
                return
            for i, card in enumerate(remaining):
                rank = card.rank
                if rank not in selected_ranks:
                    selected_ranks.add(rank)
                    backtrack(hand + [card], remaining[i + 1 :])
                    selected_ranks.remove(rank)

        results: list[Play] = []
        selected_ranks: set[str] = set()
        backtrack([], cards)
        return results

    def make_play(self, last_play: Play, start=False) -> Play:
        """Play a combination. Assumes there are choices to play."""
        plays: list[Play] = self.find_plays(last_play)
        if not plays:
            return Play([], CardCombination.PASS)
        if start:
            plays = [p for p in plays if Card("Diamonds", "3") in p.cards]
        chosen_play: Play = random.choice(plays)
        for c in chosen_play.cards:
            self.hand.remove(c)
        return chosen_play

    def has_cards(self):
        return len(self.hand) > 0


class HumanPlayer(Player):
    def make_play(self, last_play: Play, start=False) -> Play:
        """Allow a human player to input a play manually."""
        print(f"Your hand:")
        for i, card in enumerate(self.hand):
            print(f"\t{i}: {card}")
        print(f"Last play: {last_play}")

        while True:
            card_indices: str = ""
            try:
                # Prompt the user to input their play
                card_indices = input(
                    "Enter the indices of the cards you want to play, separated by spaces or 'PASS' to pass: "
                )
                # This will throw a ValueError if it cannot split
                indices = list(map(int, card_indices.split()))

                # Validate indices
                if any(i < 0 or i >= len(self.hand) for i in indices):
                    print(
                        "Invalid indices. Please enter valid indices from your hand."
                    )
                    continue

                if start and not any(
                    self.hand[i] == Card("Diamonds", "3") for i in indices
                ):
                    print(
                        "Game starting combination must include 3 of Diamonds"
                    )
                    continue

                # Create the play from the selected cards
                selected_cards = [self.hand[i] for i in indices]
                combination = identify_combination(selected_cards)

                if combination == CardCombination.INVALID:
                    print("Invalid combination. Please enter a valid play.")
                    continue

                play = Play(selected_cards, combination)

                # Check if the play is valid against the last play
                if play < last_play:
                    print(
                        "Your play is not better than the last play. Please enter a valid play."
                    )
                    continue

                # Remove the played cards from the hand
                for card in selected_cards:
                    self.hand.remove(card)

                return play

            except ValueError:
                if card_indices.lower() == "pass":
                    return Play([], CardCombination.PASS)
                print(
                    "Invalid input. Please enter numbers separated by spaces or 'PASS'."
                )


class AggressivePlayer(Player):
    def make_play(self, last_play: Play, start=False) -> Play:
        """Play the most aggressive combination."""
        plays: list[Play] = self.find_plays(last_play)
        if not plays:
            return Play([], CardCombination.PASS)
        if start:
            plays = [p for p in plays if Card("Diamonds", "3") in p.cards]
        chosen_play: Play = plays[-1]
        for c in chosen_play.cards:
            self.hand.remove(c)
        return chosen_play


class PlayItSafePlayer(Player):
    def make_play(self, last_play: Play, start=False) -> Play:
        """Play the combination that gets rid of the most low cards."""
        plays: list[Play] = self.find_plays(last_play)
        chosen_play: Play = Play()
        if not plays:
            return Play([], CardCombination.PASS)
        # If we can't control the start, play your weakest
        if not last_play.combination == CardCombination.ANY:
            chosen_play = plays[0]
        if start:
            plays = [p for p in plays if Card("Diamonds", "3") in p.cards]

        lowest_rank: str = plays[0].cards[0].rank
        chosen_play = plays[0]
        lowest_rank_freq: int = 0
        # Find which Play gets rid of the most cards with this rank
        # Only really relevant when you start a round
        for p in plays:
            lowest_rank_count = Counter([c.rank for c in p.cards])[lowest_rank]
            # Avoid starting a round with four of a kind
            if p.combination == CardCombination.FOUROFAKIND:
                break
            # Prioritize 2 or 3 of a kind
            if lowest_rank_count > lowest_rank_freq:
                lowest_rank_freq = lowest_rank_count
                chosen_play = p
            # Take the weakest full house over a triple
            elif lowest_rank_count == lowest_rank_freq and len(p.cards) > len(
                chosen_play.cards
            ):
                # Don't play a full house if any card is "good"
                if any(c.rank_index() > Card.ranks["9"] for c in p.cards):
                    continue
                chosen_play = p
        for c in chosen_play.cards:
            self.hand.remove(c)
        return chosen_play


class PlayerType(Enum):
    Random = 0
    Aggressive = 1
    PlayItSafe = 2
    RLAgent = 3
