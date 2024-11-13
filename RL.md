# Reinforcement Learning

## State (WIP)
- Count number of each combination as state (e.g. 10 singles, 4 pairs, 2 straights)
- Agent's hand and Play history 
- Every round as a state, with agents hand and the cards that are being played by other agents

## Actions
- Playing a combination
  - Reduces the count of combinations
  - Reduce Agent's hand and add played combo to Play history

## Rewards
- Reward playing cards of course
  - Weight playing more cards at a time more
  - Weight playing weaker cards more
  - Weight consecutive plays more (winning the round)
- Reward preserving as many options as possible

## Baselines
- Have each Agent (Random, Eliminate-Weakest, Aggressive) play against all Random Agents and record win rates

# THINGS TO ASK
- How to represent state
- Any good reinforcement learning frameworks we can use with a game made from scratch