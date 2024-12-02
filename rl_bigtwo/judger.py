from rlcard.games.doudizhu.utils import cards2str

class BigTwoJudger:
    """Determine which cards can be played"""
    @staticmethod
    def playable_cards_from_hand(current_hand):
        return set()
    
    def __init__(self, players, np_random):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        self.playable_cards = [set() for _ in range(3)]
        self._recorded_removed_playable_cards = [[] for _ in range(3)]
        for player in players:
            player_id = player.player_id
            current_hand = cards2str(player.current_hand)
            self.playable_cards[player_id] = self.playable_cards_from_hand(current_hand)