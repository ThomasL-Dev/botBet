import time
import threading
from db import DataBase
# ========================================== FIN DES IMPORTS ========================================================= #
db = DataBase()


class Client:
    name_id: str
    uuid: str
    db = db

    def __init__(self, name: str, uuid: str):

        self.name_id = name
        self.uuid = uuid

        # on ajoute le client a la db pour lenregistrer si il nest pas deja dedans et on ajoute les coins de depart
        self.db.insert(self.name_id, 300)

        self.coins = self.get_total_coins()

        self.__reponse = "None"

        self.have_bet = False

        self.is_connected_in_vocal = False
        self.is_deaf_in_vocal = False



    def add_coin(self, coin_to_add: int):
        self.db.update_coin(self.name_id, coin_to_add)


    def remove_coin(self, coin_to_rm: int):
        self.db.remove_coin(self.name_id, coin_to_rm)


    def set_coin(self, coin_to_rm: int):
        self.db.set_coin(self.name_id, coin_to_rm)


    def get_total_coins(self):
        return self.db.get_coins_from_name(self.name_id)


    def set_reponse(self, rep):
        self.__reponse = rep



    def get_reponse(self):
        return self.__reponse


    def reset_bet(self):
        self.set_reponse("None")
        self.have_bet = False


