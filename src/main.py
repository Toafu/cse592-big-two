from sys import argv
import logging
import gymnasium as gym
from gymnasium.envs.registration import register
from player import (
    AggressivePlayer,
    HumanPlayer,
    PlayItSafePlayer,
    Player,
    RLAgent,
)
from card import Card, CardCombination, Deck, Play, play2discrete
import json

LOGGER = logging.getLogger(__name__)


class BigTwoGame:
    def __init__(
        self,
        players: list[Player],
    ):
        self.players = players
        for i, p in enumerate(players):
            p.set_id(i)
        self.setup()

    def setup(self):
        self.deck: Deck = Deck()
        num_players = len(self.players)
        if num_players == 2:
            # Remove some cards from the deck for 2 players
            self.deck.cards = self.deck.cards[0:42]
            while Card("Diamonds", "3") not in self.deck.cards:
                self.deck = Deck()
                self.deck.cards = self.deck.cards[0:42]
        assert Card("Diamonds", "3") in self.deck.cards
        hands = self.deck.deal(num_players)

        for i, p in enumerate(self.players):
            p.set_hand(hands[i])
        # variable to track passes
        self.passes = [False] * len(self.players)

        # the current player index starts as the player with the 3 of diamonds
        for i in range(len(self.players)):
            lowestCard: Card = self.players[i].hand[0]

            if lowestCard == Card("Diamonds", "3"):
                self.current_player_index = i
                break
        self.last_play: Play = Play()
        self.last_player: int = 0
        self.turns: int = 0
        self.winner: Player | None = None

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(
            self.players
        )

    def play_turn(self):
        """Current player selects and plays a Play.

        Does not advance turn or current player.
        """
        player = self.players[self.current_player_index]
        LOGGER.info("%s's turn", player.name)
        ctx = player.find_plays(self.last_play, self.turns == 0)
        if not isinstance(player, HumanPlayer):
            LOGGER.info("%s hand: %s", player.name, player.hand)
            LOGGER.info("%s options: %s", player.name, ctx.available_plays)

        chosen_play = player.make_play(ctx)
        if not chosen_play.combination == CardCombination.PASS:
            LOGGER.info("%s plays %s", player.name, chosen_play)
            self.last_play = chosen_play
            self.last_player = self.current_player_index
            for c in chosen_play.cards:
                player.hand.remove(c)
            self.passes[self.current_player_index] = False
        else:
            LOGGER.info("%s passes", player.name)
            self.passes[self.current_player_index] = True

    def play_round(self):
        LOGGER.info("New round")
        # Check if all other players have passed their turn
        self.last_play = Play()
        self.passes = [False] * len(self.players)
        while not self.check_other_passes() and not self.is_game_over():
            self.play_turn()
            self.next_player()
            self.turns += 1
        LOGGER.info("Round over\n")

    # function to check if all the other players have passed their turn
    def check_other_passes(self):
        """Returns true if all players but one pass in a row."""
        for i, has_passed in enumerate(self.passes):
            # Skip current player and check if any other player hasn't passed
            if i != self.current_player_index and not has_passed:
                return False
        return True

    def is_game_over(self):
        game_over: bool = any(
            not player.has_cards() for player in self.players
        )
        if game_over:
            for p in self.players:
                if not p.has_cards():
                    self.winner = p
                    break
        return game_over

    def start(self):
        LOGGER.info("Starting Big Two Game!")

        while not self.is_game_over():
            self.play_round()

        LOGGER.info("Game Over!")
        for player in self.players:
            if not player.has_cards():
                LOGGER.info("%s has won the game!", player.name)
                return player
        assert False, "No winner after game ended"


def get_greedy_statistics():
    games: int = 1000
    random_won: int = 0
    aggro_won: int = 0
    safe_won: int = 0
    safe_won_1v1: int = 0

    for i in range(games):
        game = BigTwoGame(
            [
                AggressivePlayer(name="Aggressive0"),
                Player(name="Random1"),
                Player(name="Random2"),
                Player(name="Random3"),
            ]
        )
        winner: str = game.start().name
        if winner == "Aggressive0":
            aggro_won += 1

        game = game = BigTwoGame(
            [
                PlayItSafePlayer(name="PlayItSafe0"),
                Player(name="Random1"),
                Player(name="Random2"),
                Player(name="Random3"),
            ]
        )
        winner: str = game.start().name
        if winner == "PlayItSafe0":
            safe_won += 1

        game = BigTwoGame(
            [
                Player(name="Random0"),
                Player(name="Random1"),
                Player(name="Random2"),
                Player(name="Random3"),
            ]
        )
        winner: str = game.start().name
        if winner == "Random0":
            random_won += 1

        game = BigTwoGame(
            [PlayItSafePlayer(name="PlayItSafe0"), Player(name="Random1")]
        )
        winner: str = game.start().name
        if winner == "PlayItSafe0":
            safe_won_1v1 += 1

    print(f"Random won {random_won}/{games} games against 3 random agents")
    print(f"Aggressive won {aggro_won}/{games} games against 3 random agents")
    print(f"Safe won {safe_won}/{games} games against 3 random agents")
    print(f"Safe_1v1 won {safe_won_1v1}/{games} games against 1 random agent")


if __name__ == "__main__":
    if len(argv) > 1 and argv[1].lower() == "info":
        logging.basicConfig(level=logging.INFO)

    rl_agent = RLAgent(name="RLAgent", hand=[], id=-1)
    random_agent = Player(name="Random1")

    game: BigTwoGame = BigTwoGame([rl_agent, random_agent])
    register(
        id="BigTwoRL",
        entry_point="env:BigTwoEnv",
    )

    from env import BigTwoEnv

    num_episodes = 100

    # Make the env
    env = gym.make("BigTwoRL", game=game)
    assert isinstance(env.unwrapped, BigTwoEnv)
    # Get our agents
    for episode in range(num_episodes):
        obs, info = env.reset()
        agents = game.players
        done = False

        # Each iteration should start when it's our agent's turn
        while not done:
            agent = agents[game.current_player_index]
            assert isinstance(agent, RLAgent)
            turn_context = agent.find_plays(game.last_play, game.turns == 0)
            play = agent.make_play(turn_context, obs)
            action = play2discrete(play)
            next_obs, reward, done, _, info = env.step(action)

            agent.update(
                obs,
                action,
                reward,
                done,
                next_obs,
                env.unwrapped._get_info(),
            )
            rl_agent.decay_epsilon()

            obs = next_obs

        LOGGER.info(
            "%s has won the game!", agents[game.current_player_index].name
        )

        game.setup()
    #Save q table
    with open("data.py", "w") as out:
        out.write(str(rl_agent.q_values))
    # exit(0)

    # Evaluate the agent
    print(f"Agent has explored {len(rl_agent.q_values)} states")
    actions = 0
    for s in rl_agent.q_values:
        actions += len(s)
    print(f"Within these states, the agent has taken {actions} action-likes")
    num_trials = 100
    wins = 0

    game: BigTwoGame = BigTwoGame([rl_agent, random_agent])
    env = gym.make("BigTwoRL", game=game)
    assert isinstance(env.unwrapped, BigTwoEnv)

    for _ in range(num_trials):
        obs, info = env.reset()
        agents = game.players
        done = False

        while not done:
            agent = agents[game.current_player_index]
            turn_context = agent.find_plays(game.last_play, game.turns == 0)
            if isinstance(agent, RLAgent):
                play = agent.make_play(turn_context, obs)
            else:
                play = agent.make_play(turn_context)
            action = play2discrete(play)
            next_obs, reward, done, _, info = env.step(action)

            obs = next_obs

        LOGGER.info(
            "%s has won the game!", agents[game.current_player_index].name
        )
        if game.current_player_index == env.unwrapped.rl_agentid:
            wins += 1

        game.setup()

    print(f"RLAgent won {wins}/{num_trials} games against 1 random agent")

