from player import AggressivePlayer, HumanPlayer, Player
from card import Card, CardCombination, Deck, Play, identify_combination


class BigTwoGame:
    def __init__(self):
        self.deck = Deck()
        hands = self.deck.deal(4)
        self.players: list[Player] = [
            AggressivePlayer("Aggro Computer", hands[0]),
            Player("Computer 1", hands[1]),
            Player("Computer 2", hands[2]),
            Player("Computer 3", hands[3]),
        ]
        # hands = self.deck.deal(2)
        # self.players: list[Player] = [
        #     HumanPlayer("Player1", hands[0]),
        #     HumanPlayer("Player2", hands[1]),
        # ]
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

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )

    def play_round(self):
        print("New round")
        # Check if all other players have passed their turn
        self.last_play = Play()
        self.passes = [False] * len(self.players)
        while not self.check_other_passes() and not self.is_game_over():
            player = self.players[self.current_player_index]
            print(f"{player.name}'s turn")
            print("Current Combination:", self.last_play.combination)
            plays: list[Play] = player.find_plays(self.last_play)

            if plays:
                if not isinstance(player, HumanPlayer):
                    print(f"{player.name} hand: {player.hand}")
                    print(f"{player.name} options: {plays}")
                self.last_play = player.make_play(self.last_play)
                print(f"{player.name} plays {self.last_play}")
                self.passes[self.current_player_index] = False
            else:
                print(f"{player.name} passes")
                self.passes[self.current_player_index] = True

            self.next_player()
        print("Round over\n")

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
        print("Starting Big Two Game!")

        while not self.is_game_over():
            self.play_round()

        print("Game Over!")
        for player in self.players:
            if not player.has_cards():
                print(f"{player.name} has won the game!")
                break


if __name__ == "__main__":
    game = BigTwoGame()
    game.start()
