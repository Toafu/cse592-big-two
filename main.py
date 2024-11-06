from collections import Counter
from player import HumanPlayer, Player
from card import Card, CardCombination, Deck


# Game Class
class BigTwoGame:
    def __init__(self):
        self.deck = Deck()
        hands = self.deck.deal(4)
        self.players = [
            HumanPlayer("You", hands[0]),
            Player("Computer 1", hands[1]),
            Player("Computer 2", hands[2]),
            Player("Computer 3", hands[3]),
        ]
        self.current_player_index = 0
        self.last_play = None
        self.current_combination = CardCombination.ANY

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )

    def play_round(self):
        player = self.players[self.current_player_index]
        print(f"\n{player.name}'s turn")

        play = player.find_play(self.last_play)
        if play:
            print(f"{player.name} plays: {play}")
            self.last_play = [play]
        else:
            print(f"{player.name} passes")

        self.next_player()

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


# Run the game
if __name__ == "__main__":
    game = BigTwoGame()
    game.start()
