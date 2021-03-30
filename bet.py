from typing import NamedTuple
import datetime

# ========================================== FIN DES IMPORTS ========================================================= #


class ClientBet(NamedTuple):
    name: str
    reponse: str
    nb_coins: str


class Bet:

    _BET_IS_ALIVE = False
    _BET_LOCKED = False

    _BET_UTTERANCE = None

    _BETS_LIST = []

    _NAME_REPONSES = None

    _CORRECT_REPONSE = None

    _INIT_BET_DATETIME = utc_datetime = datetime.datetime.utcnow()

    _UUID: str
    _ID: str

    _OWNER = "None"

    _WINNERS = []
    _LOOSERS = []

    _COTE_R_1 = {'rep': "1️⃣", 'count': 0, 'total': 0}
    _COTE_R_2 = {'rep': "2️⃣", 'count': 0, 'total': 0}



    def __init__(self, user_input: str):

        self._USER_INPUT = user_input

        self._BET_DATE = self.get_bet_date()

        self._NAME_REPONSES = self._find_bet_reponses()  # return oui, non
        self._BET_UTTERANCE = self._find_bet_phrase()

        self._REPONSE_1 = {"name": self._NAME_REPONSES[0], "emoticon": "1️⃣"}  # 1️⃣   👍
        self._REPONSE_2 = {"name": self._NAME_REPONSES[1], "emoticon": "2️⃣"}  # 2️⃣   👎

        print("[BET START] name :", self._BET_UTTERANCE, "| reponses :", self._REPONSE_1, self._REPONSE_2)



    def do_bet(self, bet: ClientBet):
        if not self._BET_LOCKED:
            self._BETS_LIST.append(bet)
            self.add_to_cote(bet)



    def add_to_cote(self, bet: ClientBet):
        if bet.reponse in self._REPONSE_1['name'] or bet.reponse == self._REPONSE_1['emoticon']:
            self._COTE_R_1['total'] = int(self._COTE_R_1['total']) + int(bet.nb_coins)
            self._COTE_R_1['count'] = int(self._COTE_R_1['count']) + 1

        elif bet.reponse in self._REPONSE_2['name'] or bet.reponse == self._REPONSE_2['emoticon']:
            self._COTE_R_2['total'] = int(self._COTE_R_2['total']) + int(bet.nb_coins)
            self._COTE_R_2['count'] = int(self._COTE_R_2['count']) + 1

        else:
            pass



    def get_cote(self):
        return "votes: " + str(self._COTE_R_1['count']) + "\ncoins: " + str(self._COTE_R_1['total']), "votes: " + str(self._COTE_R_2['count']) + "\ncoins: " + str(self._COTE_R_2['total'])



    def lock(self):
        self._BET_LOCKED = True

    def is_locked(self):
        return self._BET_LOCKED


    def stop(self):
        print("[BET STOP] name :", self._BET_UTTERANCE, "| correct reponse :", self._CORRECT_REPONSE)
        self._INIT_BET_DATETIME = None
        self._BET_UTTERANCE = None
        self._NAME_REPONSES = None
        self._CORRECT_REPONSE = None
        self._UUID = "0"
        self._ID = "0"
        self._OWNER = "None"
        self._BETS_LIST.clear()
        self._BET_LOCKED = False
        self._BET_IS_ALIVE = False
        self._COTE_R_1['total'] = 0
        self._COTE_R_1['count'] = 0
        self._COTE_R_2['total'] = 0
        self._COTE_R_2['count'] = 0
        self._WINNERS.clear()
        self._LOOSERS.clear()


    def set_correct_reponse(self, rep: str):
        if rep.lower() in self._REPONSE_1['name'].lower() or rep == self._REPONSE_1['emoticon']:
            self._CORRECT_REPONSE = self._REPONSE_1['emoticon']

        elif rep.lower() in self._REPONSE_2['name'].lower() or rep == self._REPONSE_2['emoticon']:
            self._CORRECT_REPONSE = self._REPONSE_2['emoticon']


    def get_winners(self):
        return self._WINNERS


    def get_loosers(self):
        return self._LOOSERS


    def get_correct_reponse(self):
        return self._CORRECT_REPONSE


    def player_names_of_the_bet(self):
        out = []
        for client_bet in self._BETS_LIST:
            bet_client_name = client_bet.name
            out.append(bet_client_name)

        return out


    def get_owner(self):
        return str(self._OWNER)


    def get_bet_list(self):
        return self._BETS_LIST


    def get_infos(self):
        return self._BET_UTTERANCE, self._NAME_REPONSES, self._ID


    def get_utterance(self):
        return self._BET_UTTERANCE


    def get_reponse_1(self):
        return self._REPONSE_1


    def get_reponse_2(self):
        return self._REPONSE_2


    def get_bet_date(self):
        return self._INIT_BET_DATETIME.strftime("%d/%m/%Y à %H:%M:%S")


    def set_id(self, id: str):
        self._ID = id


    def get_id(self):
        return self._ID


    def set_uuid(self, uuid: str):
        self._UUID = uuid


    def get_uuid(self):
        return self._UUID


    def set_owner(self, owner: str):
        self._OWNER = owner



    def calcul_payout(self):
        # calcul le total des coins parié
        total_all_coins = sum(int(x.nb_coins) for x in self._BETS_LIST)

        # calcul des coins total des votant gagnant
        winner_total_coins = sum(int(x.nb_coins) for x in self._BETS_LIST if x.reponse == self._CORRECT_REPONSE)

        # on add les coins a tout les winners
        # en fonction de se qui ont voté
        payout = []
        for client_bet in self._BETS_LIST:
            bet_client_name = client_bet.name
            bet_client_voted_for = client_bet.reponse
            bet_client_voted_coins = client_bet.nb_coins

            client_bet_info = (str(bet_client_name), str(bet_client_voted_for), str(bet_client_voted_coins))

            if bet_client_voted_for in self._CORRECT_REPONSE:
                # les total des coins sont divisé entre chaque gagnant en fonction de se qu'il on voté
                _payout = int(total_all_coins * int(bet_client_voted_coins) / winner_total_coins)

                payout.append((bet_client_name, _payout))
                self._WINNERS.append(client_bet_info)

            else:
                self._LOOSERS.append(client_bet_info)

        return payout



    def _find_bet_reponses(self):
        default_reponses = "oui", "non"
        if self._check_if_utterance_is_ok():
            splitter = None

            if ', ' in self._USER_INPUT:
                splitter = ', '

            elif ',' in self._USER_INPUT:
                splitter = ','

            r = self._USER_INPUT
            if splitter is not None:
                r = r.split(splitter)[1]

            if "/" in r:
                r1 = r.split("/")[0]
                if r1[0] == " ":
                    r1 = r1[-1:]

                r2 = r.split("/")[1]
                if r2[0] == " ":
                    r2 = r2[-1:]

                return r1, r2

            else:
                return default_reponses

        else:
            return default_reponses



    def _find_bet_phrase(self):
        if self._check_if_utterance_is_ok():

            phrase = self._USER_INPUT.split(',')[0]

            return phrase
        else:
            phrase = self._USER_INPUT
            return phrase



    def _check_if_utterance_is_ok(self):
        if "," in self._USER_INPUT:
            return True
        else:
            return None









