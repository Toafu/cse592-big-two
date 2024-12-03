from main import *

s = set()
p = Player("", Deck().cards)
plays = p.find_plays(Play())
print(f"Total number of possible plays = {len(plays)}")

for play in plays:
    s.add(play.simplify_play())

print(f"Total number of simplified plays: {len(s)}")
print(sorted(s, key=lambda x: len(x)))
