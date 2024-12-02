import numpy as np
import gymnasium as gym
from gymnasium import spaces

num_cards = 52
num_plays = 12743


class BigTwoEnv(gym.Env):
    def __init__(self, num_agents=2, rl_agentid=0) -> None:
        self.num_agents: int = num_agents
        self.rl_agentid: int = rl_agentid

        self.action_space = spaces.Discrete(num_plays)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(num_cards,), dtype=np.float32
        )

        self.reset()
