from bet import Bet
# ========================================== FIN DES IMPORTS ========================================================= #


class BetHandler:

    _BETS_COUNT = 0

    _BET_LIST = []

    def add_bet(self, bet: Bet):
        bet.set_id(str(self._BETS_COUNT))
        self._BET_LIST.append(bet)
        self._BETS_COUNT += 1


    def get_bet_from_uuid(self, uuid: str):
        for bet in self._BET_LIST:
            bet_uuid = str(bet.get_uuid())
            if bet_uuid in uuid:
                return bet


    def get_bet_from_id(self, id: str):
        for bet in self._BET_LIST:
            bet_id = str(bet.get_id())
            if bet_id in id:
                return bet


    def get_bet_from_owner(self, owner: str):
        for bet in self._BET_LIST:
            bet_owner = str(bet.get_owner())
            if bet_owner in owner:
                return bet



    def get_all_bets(self):
        return self._BET_LIST



    def remove_bet(self, uuid: str):
        for bet in self._BET_LIST:
            if str(bet.get_uuid()) in str(uuid):
                self._BET_LIST.remove(bet)
                return
