from bisect import bisect_left, bisect_right
from collections import deque, defaultdict
from dataclasses import dataclass, field
import itertools
import typing
import random
from card import *
import gymnasium as gym


Cards = typing.List[Card]


@dataclass
class TurnContext:
    """Contains available plays, the last play, and game start status."""

    available_plays: list[Play] = field(default_factory=list)
    last_play: Play = field(default_factory=Play)
    game_start: bool = False


class Player:
    """The base player acts randomly."""

    def __init__(self, *, name, hand=[], id=0):
        self.name: str = name
        self.hand: Cards = sorted(hand)
        self.id: int = id

    def set_hand(self, hand):
        self.hand = sorted(hand)

    def set_id(self, id: int):
        self.id = id

    def find_plays(
        self, last_play: Play = Play(), game_start=False
    ) -> TurnContext:
        """
        Return all valid plays compatible with the current combination.

        Filter out all plays worse than last_play.
        If start is True, consider only plays with 3 of Diamonds
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
                    possible_plays = self._get_straight_combinations_(
                        list(straight_buffer)
                    )
                    for p in possible_plays:
                        if last_play < p:
                            moves.append(p)
                case CardCombination.FOUROFAKIND:
                    moves += self._find_four_of_a_kinds_(last_play)
        if game_start:
            moves = [m for m in moves if Card("Diamonds", "3") in m.cards]
        return TurnContext(moves, last_play, game_start)

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
            if len(hand) == 5 and is_straight(hand):
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

    def make_play(self, ctx: TurnContext) -> Play:
        """Play a combination and remove cards from hand."""
        if not ctx.available_plays:
            return Play([], CardCombination.PASS)
        chosen_play: Play = random.choice(ctx.available_plays)
        return chosen_play

    def has_cards(self):
        return len(self.hand) > 0


class HumanPlayer(Player):
    def make_play(self, ctx: TurnContext) -> Play:
        """Allow a human player to input a play manually."""
        print(f"Your hand:")
        for i, card in enumerate(self.hand):
            print(f"\t{i}: {card}")
        print(f"Last play: {ctx.last_play}")

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

                if ctx.game_start and not any(
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
                if play < ctx.last_play:
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
    def make_play(self, ctx: TurnContext) -> Play:
        """Play the most aggressive combination."""
        if not ctx.available_plays:
            return Play([], CardCombination.PASS)
        chosen_play: Play = ctx.available_plays[-1]
        return chosen_play


class PlayItSafePlayer(Player):
    def make_play(self, ctx: TurnContext) -> Play:
        """Play the combination that gets rid of the most low cards."""
        chosen_play: Play = Play()
        if not ctx.available_plays:
            return Play([], CardCombination.PASS)
        # If we can't control the start, play your weakest
        if not ctx.last_play.combination == CardCombination.ANY:
            chosen_play = ctx.available_plays[0]
        if ctx.game_start:
            ctx.available_plays = [
                p
                for p in ctx.available_plays
                if Card("Diamonds", "3") in p.cards
            ]

        lowest_rank: str = ctx.available_plays[0].cards[0].rank
        chosen_play = ctx.available_plays[0]
        lowest_rank_freq: int = 0
        # Find which Play gets rid of the most cards with this rank
        # Only really relevant when you start a round
        for p in ctx.available_plays:
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
        return chosen_play


# env = gym.make("BigTwoEnv", sab=True)
# done = False
# observation, info = env.reset()
# action = env.action_space.sample()
# observation, reward, terminated, truncated, info = env.step(action)


class RLAgent(Player):
    def __init__(
        self,
        name,
        hand,
        id,
        # env: BigTwoEnv,
        alpha=0.1,
        initial_epsilon=1.0,
        epsilon_decay=0.1,
        final_epsilon=0.1,
        gamma: float = 0.9,
    ):
        super().__init__(name=name, hand=hand, id=id)

        self.q_values = defaultdict(lambda: defaultdict(float))
        self.alpha = alpha
        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon
        self.gamma = gamma
        self.play_history: list[Play] = []

    def make_obs_hashable(self, obs):
        return (
            tuple(obs[0]),
            tuple(obs[1]),
            tuple(obs[2]),
            tuple(obs[3]),
            obs[4],
        )

    def make_play(self, ctx: TurnContext, obs=None) -> Play:
        assert obs
        obs = self.make_obs_hashable(obs)
        if not ctx.available_plays:
            chosen_play = Play([], CardCombination.PASS)

        if np.random.random() < self.epsilon:
            # Random action
            chosen_play = super().make_play(ctx)
        else:
            if obs not in self.q_values:
                chosen_play = super().make_play(ctx)
            q_obs = self.q_values[obs]
            best_q: float = max(q_obs)
            best_actions = [k for k, v in q_obs.items() if v == best_q]
            best_action: tuple = random.choice(best_actions)
            best_action_cards = box2cards(best_action)
            chosen_play = Play(
                best_action_cards, identify_combination(best_action_cards)
            )

        if chosen_play.combination != CardCombination.PASS:
            self.play_history.append(chosen_play)

        return chosen_play

    def update(self, obs, action, reward, done: bool, next_obs, info):
        action = tuple(action)
        obs = self.make_obs_hashable(obs)
        next_obs = self.make_obs_hashable(next_obs)
        q_next_obs = (
            max(self.q_values[next_obs].values())
            if self.q_values[next_obs]
            else 0
        )
        future_q_value = (not done) * q_next_obs
        if done:
            # Can only get here if this agent ends the game
            reward += 100
        temporal_difference = (
            reward + self.gamma * future_q_value - self.q_values[obs][action]
        )

        self.q_values[obs][action] = (
            self.q_values[obs][action] + self.alpha * temporal_difference
        )

    def decay_epsilon(self, step):
        return self.final_epsilon + (self.epsilon - self.epsilon) * (
            1 / (1 + self.epsilon_decay * step)
        )


class PlayerType(Enum):
    Random = 0
    Aggressive = 1
    PlayItSafe = 2
    RLAgent = 3
