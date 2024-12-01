from ..main import *

class BigTwoGameSimplified:
    def __init__(
        self,
        num_players: int = 2,
        player_types: list[PlayerType] = [PlayerType.Random] * 2,
    ):
        assert num_players == len(player_types)
        self.deck = Deck()
        # Remove 10 cards from the deck
        self.deck.cards = self.deck.cards[10:]
        hands = self.deck.deal(num_players)
        self.players: list[Player] = []
        for i in range(num_players):
            match player_types[i]:
                case PlayerType.Random:
                    self.players.append(Player(f"Random{i}", hands[i]))
                case PlayerType.Aggressive:
                    self.players.append(
                        AggressivePlayer(f"Aggressive{i}", hands[i])
                    )
                case PlayerType.PlayItSafe:
                    self.players.append(
                        PlayItSafePlayer(f"PlayItSafe{i}", hands[i])
                    )
                case PlayerType.RLAgent:
                    # TODO: IMPLEMENT RLAGENT
                    self.players.append(Player(f"Random{i}", hands[i]))

        # variable to track passes
        self.passes = [False] * len(self.players)

        # the current player index starts as the player with the 3 of diamonds
        for i in range(len(self.players)):
            lowestCard: Card = self.players[i].hand[0]

            if lowestCard == Card("Diamonds", "3"):
                self.current_player_index = i
                break
        self.last_play: Play = Play()
        self.current_combination = CardCombination.ANY
        self.turns: int = 0
        self.winner: int | None = None

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )

    def play_round(self):
        LOGGER.info("New round")
        # Check if all other players have passed their turn
        self.last_play = Play()
        self.passes = [False] * len(self.players)
        while not self.check_other_passes() and not self.is_game_over():
            player = self.players[self.current_player_index]
            LOGGER.info("%s's turn", player.name)
            if not isinstance(player, HumanPlayer):
                LOGGER.info("%s hand: %s", player.name, player.hand)
                plays: list[Play] = player.find_plays(self.last_play)
                if self.turns == 0:
                    plays = [
                        p for p in plays if Card("Diamonds", "3") in p.cards
                    ]
                LOGGER.info("%s options: %s", player.name, plays)

            chosen_play = player.make_play(self.last_play, self.turns == 0)
            if not chosen_play.combination == CardCombination.PASS:
                self.last_play = chosen_play
                LOGGER.info("%s plays %s", player.name, self.last_play)
                self.passes[self.current_player_index] = False
            else:
                LOGGER.info("%s passes", player.name)
                self.passes[self.current_player_index] = True

            self.next_player()
            self.turns += 1
        LOGGER.info("Round over\n")

    # function to check if all the other players have passed their turn
    def check_other_passes(self):
        for i, has_passed in enumerate(self.passes):
            # Skip current player and check if any other player hasn't passed
            if i != self.current_player_index and not has_passed:
                return False
        return True

    def is_game_over(self):
        return any(not player.has_cards() for player in self.players)

    def start(self):
        LOGGER.info("Starting Big Two Game!")

        while not self.is_game_over():
            self.play_round()

        LOGGER.info("Game Over!")
        for i, player in enumerate(self.players):
            if not player.has_cards():
                LOGGER.info("%s has won the game!", player.name)
                self.winner = i
        assert False, "No winner after game ended"
