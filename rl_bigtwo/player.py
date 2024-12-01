class BigTwoPlayer:
    def __init__(self, player_id, np_random):
        ''' Give the player an id in one game

        Args:
            player_id (int): the player_id of a player

        Notes:
            1. role: A player's temporary role in one game(landlord or peasant)
            2. played_cards: The cards played in one round
            3. hand: Initial cards
            4. _current_hand: The rest of the cards after playing some of them
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.initial_hand: str = ''
        self._current_hand = []
        self.played_cards = None
        self.singles = '3456789TJQKA2BR'

        #record cards removed from self._current_hand for each play()
        # and restore cards back to self._current_hand when play_back()
        self._recorded_played_cards = []

    @property
    def get_hand(self):
        return self._current_hand
    
    def set_hand(self, hand):
        self._current_hand = hand