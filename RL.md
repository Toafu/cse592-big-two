# Reinforcement Learning

## State
- Agent's hand, last Play, and Play history?
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

# It's okay to simplify the game
- We have to represent state as the hand
- If we are the first, we can be novel
- Bring it down to two players and reduce the deck size
- Look up on our own RL stuff
