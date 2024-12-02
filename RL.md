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


# All Simplified Plays
```
360 total plays
['2', '22', '222', '22333', '22444', '22555', '22666', '22777', '22888',
'22999', '22AAA', '22JJJ', '22KKK', '22QQQ', '22TTT', '23333', '24444', '25555',
'26666', '27777', '28888', '29999', '2AAAA', '2JJJJ', '2KKKK', '2QQQQ', '2TTTT',
'3', '32222', '33', '33222', '333', '33444', '33555', '33666', '33777', '33888',
'33999', '33AAA', '33JJJ', '33KKK', '33QQQ', '33TTT', '34444', '34567', '35555',
'36666', '37777', '38888', '39999', '3AAAA', '3JJJJ', '3KKKK', '3QQQQ', '3TTTT',
'4', '42222', '43333', '44', '44222', '44333', '444', '44555', '44666', '44777',
'44888', '44999', '44AAA', '44JJJ', '44KKK', '44QQQ', '44TTT', '45555', '45678',
'46666', '47777', '48888', '49999', '4AAAA', '4JJJJ', '4KKKK', '4QQQQ', '4TTTT',
'5', '52222', '53333', '54444', '55', '55222', '55333', '55444', '555', '55666',
'55777', '55888', '55999', '55AAA', '55JJJ', '55KKK', '55QQQ', '55TTT', '56666',
'56789', '57777', '58888', '59999', '5AAAA', '5JJJJ', '5KKKK', '5QQQQ', '5TTTT',
'6', '62222', '63333', '64444', '65555', '66', '66222', '66333', '66444',
'66555', '666', '66777', '66888', '66999', '66AAA', '66JJJ', '66KKK', '66QQQ',
'66TTT', '67777', '6789T', '68888', '69999', '6AAAA', '6JJJJ', '6KKKK', '6QQQQ',
'6TTTT', '7', '72222', '73333', '74444', '75555', '76666', '77', '77222',
'77333', '77444', '77555', '77666', '777', '77888', '77999', '77AAA', '77JJJ',
'77KKK', '77QQQ', '77TTT', '78888', '789TJ', '79999', '7AAAA', '7JJJJ', '7KKKK',
'7QQQQ', '7TTTT', '8', '82222', '83333', '84444', '85555', '86666', '87777',
'88', '88222', '88333', '88444', '88555', '88666', '88777', '888', '88999',
'88AAA', '88JJJ', '88KKK', '88QQQ', '88TTT', '89999', '89TJQ', '8AAAA', '8JJJJ',
'8KKKK', '8QQQQ', '8TTTT', '9', '92222', '93333', '94444', '95555', '96666',
'97777', '98888', '99', '99222', '99333', '99444', '99555', '99666', '99777',
'99888', '999', '99AAA', '99JJJ', '99KKK', '99QQQ', '99TTT', '9AAAA', '9JJJJ',
'9KKKK', '9QQQQ', '9TJQK', '9TTTT', 'A', 'A2222', 'A3333', 'A4444', 'A5555',
'A6666', 'A7777', 'A8888', 'A9999', 'AA', 'AA222', 'AA333', 'AA444', 'AA555',
'AA666', 'AA777', 'AA888', 'AA999', 'AAA', 'AAJJJ', 'AAKKK', 'AAQQQ', 'AATTT',
'AJJJJ', 'AKKKK', 'AQQQQ', 'ATTTT', 'J', 'J2222', 'J3333', 'J4444', 'J5555',
'J6666', 'J7777', 'J8888', 'J9999', 'JAAAA', 'JJ', 'JJ222', 'JJ333', 'JJ444',
'JJ555', 'JJ666', 'JJ777', 'JJ888', 'JJ999', 'JJAAA', 'JJJ', 'JJKKK', 'JJQQQ',
'JJTTT', 'JKKKK', 'JQKA2', 'JQQQQ', 'JTTTT', 'K', 'K2222', 'K3333', 'K4444',
'K5555', 'K6666', 'K7777', 'K8888', 'K9999', 'KAAAA', 'KJJJJ', 'KK', 'KK222',
'KK333', 'KK444', 'KK555', 'KK666', 'KK777', 'KK888', 'KK999', 'KKAAA', 'KKJJJ',
'KKK', 'KKQQQ', 'KKTTT', 'KQQQQ', 'KTTTT', 'Q', 'Q2222', 'Q3333', 'Q4444',
'Q5555', 'Q6666', 'Q7777', 'Q8888', 'Q9999', 'QAAAA', 'QJJJJ', 'QKKKK', 'QQ',
'QQ222', 'QQ333', 'QQ444', 'QQ555', 'QQ666', 'QQ777', 'QQ888', 'QQ999', 'QQAAA',
'QQJJJ', 'QQKKK', 'QQQ', 'QQTTT', 'QTTTT', 'T', 'T2222', 'T3333', 'T4444',
'T5555', 'T6666', 'T7777', 'T8888', 'T9999', 'TAAAA', 'TJJJJ', 'TJQKA', 'TKKKK',
'TQQQQ', 'TT', 'TT222', 'TT333', 'TT444', 'TT555', 'TT666', 'TT777', 'TT888',
'TT999', 'TTAAA', 'TTJJJ', 'TTKKK', 'TTQQQ', 'TTT']
```
