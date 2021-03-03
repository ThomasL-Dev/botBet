import time
import threading
from db import DataBase
# ========================================== FIN DES IMPORTS ========================================================= #
db = DataBase()






class Client:
    name_id: str
    db = db

    def __init__(self, name: str):

        self.name_id = name

        self.db.insert(self.name_id)

        self.coins = self.get_total_coins()

        self.__reponse = None

        self.have_bet = False

        self.is_adding_coin = False
        self.thread_adding_coins = AddingCoinsService(self.name_id)
        self.thread_adding_coins.start()
        self.thread_adding_coins.pause()


    def start_adding_coins(self, coin_to_add: int):
        self.thread_adding_coins.resume(coin_to_add)
        self.is_adding_coin = True
        # print("[CLIENT INFO]", "starting to adding coin for", self.name_id)


    def stop_adding_coin(self):
        self.thread_adding_coins.pause()
        self.is_adding_coin = False
        # print("[CLIENT INFO]", "stopping to adding coin for", self.name_id)


    def add_coin(self, coin_to_add: int):
        self.db.update_coin(self.name_id, coin_to_add)


    def remove_coin(self, coin_to_rm: int):
        self.db.remove_coin(self.name_id, coin_to_rm)


    def get_total_coins(self):
        return self.db.get_coins_from_name(self.name_id)


    def set_reponse(self, rep):
        self.__reponse = rep


    def get_reponse(self):
        return self.__reponse




class AddingCoinsService(threading.Thread):
    db = db

    def __init__(self, name_id: str):
        threading.Thread.__init__(self)

        self.name_id = name_id

        self.is_adding_coin = False

        self.coin_to_add = 0


        #flag to pause thread
        self.paused = False

        self.pause_cond = threading.Condition(threading.Lock())


    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()

                #thread should do the thing if
                #not paused
                if self.is_adding_coin:
                    time.sleep(300)
                    self.add_coin(self.coin_to_add)
                else:
                    time.sleep(2)


    def pause(self):
        self.is_adding_coin = False
        self.paused = True
        self.pause_cond.acquire()


    def resume(self, coin_to_add: int):
        self.coin_to_add = coin_to_add

        self.is_adding_coin = True
        self.paused = False

        self.pause_cond.notify()
        self.pause_cond.release()


    def add_coin(self, coin_to_add: int):
        self.db.update_coin(self.name_id, coin_to_add)


    def pause_a_while(self):
        threading.Timer(10).start()


