from player import HumanPlayer, Player
from card import Card, CardCombination, Deck, Play, identify_combination


class BigTwoGame:
    def __init__(self):
        self.deck = Deck()
        # hands = self.deck.deal(4)
        # self.players: list[Player] = [
        #     HumanPlayer("You", hands[0]),
        #     Player("Computer 1", hands[1]),
        #     Player("Computer 2", hands[2]),
        #     Player("Computer 3", hands[3]),
        # ]
        hands = self.deck.deal(2)
        self.players: list[Player] = [
            HumanPlayer("Player1", hands[0]),
            HumanPlayer("Player2", hands[1]),
        ]
        # variable to track passes
        self.passes = [False] * len(self.players)

        # the current player index would be for the player holding the 3 of diamonds
        # check for 3 of diamonds
        for i in range(len(self.players)):
            lowestCard = self.players[i].hand[0]

            if lowestCard.suit == "Diamonds" and lowestCard.rank == "3":
                self.current_player_index = i
        self.last_play: Play = Play([], CardCombination.ANY)
        self.current_combination = CardCombination.ANY

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )

    def play_round(self):
        # to check if all other players have passed their turn
        if self.check_other_passes():
            print("All other players have passed ")
            print("Now the player can decide which combination to play")
            self.current_combination = CardCombination.ANY
        player = self.players[self.current_player_index]
        print(f"\n{player.name}'s turn")
        print("Current Combination:", self.current_combination.name)
        play = player.find_plays(self.last_play)

        if play:
            print(f"{player.name} plays: {play}")
            # TODO: FIX THIS BANDAID
            self.last_play = Play(
                list(play[0]), identify_combination(list(play[0]))
            )
        else:
            print(f"{player.name} passes")
            self.passes[self.current_player_index] = True

        self.next_player()

    # function to check if all the other players have passed their turn
    def check_other_passes(self):
        for i, has_passed in enumerate(self.passes):
            # Skip the current player and check if any other player has not passed
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
