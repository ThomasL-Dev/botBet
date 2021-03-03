import os
import sqlite3


# ========================================== FIN DES IMPORTS ========================================================= #


class DataBase:

    def __init__(self):
        self.DB_CLIENT = 'client.db'

    def create(self):
        try:
            db = sqlite3.connect(self.DB_CLIENT)
            db.execute("""
                            CREATE TABLE IF NOT EXISTS client(
                                 name TEXT PRIMARY KEY UNIQUE,
                                 coin INT
                            )
                            """)
            db.commit()
            db.close()

            print("[DB INFO]", "db '" + self.DB_CLIENT + "' created")

        except Exception as e:
            print("[DB CREATE ERROR]", e)
            pass


    def insert(self, name: str):
        try:
            dict_data = {'name': name, 'coin': 0}
            db = sqlite3.connect(self.DB_CLIENT, timeout=1)
            db.execute("INSERT INTO client(name, coin) VALUES(:name, :coin)", dict_data)
            db.commit()
            db.close()
            print("[DB INFO]", name + " inserted to '" + self.DB_CLIENT + "'")

        except sqlite3.IntegrityError:
            # print("DB ALERT :", name, "already in db")
            pass

        except Exception as e:
            print("[DB INSERT ERROR]", e)
            pass




    def update_coin(self, name: str, coin_to_add: int):
        try:
            db = sqlite3.connect(self.DB_CLIENT)
            cur = db.cursor()
            cur.execute("""UPDATE client SET coin = coin + ? WHERE name = ?""", (coin_to_add, name, ))

            db.commit()
            db.close()
            print("[DB INFO]", "adding", coin_to_add, "coins to '" + name + "'")

        except Exception as e:
            print("[DB UPDATE COIN ERROR]", e)
            pass



    def remove_coin(self, name: str, coin_to_remove: int):
        try:
            db = sqlite3.connect(self.DB_CLIENT)
            cur = db.cursor()
            cur.execute("""UPDATE client SET coin = coin - ? WHERE name = ?""", (coin_to_remove, name, ))

            db.commit()
            db.close()
            print("[DB INFO]", "removing", coin_to_remove, "coins to '" + name + "'")

        except Exception as e:
            print("[DB REMOVE COIN ERROR]", e)
            pass




    def get_coins_from_name(self, name: str):
        try:
            db = sqlite3.connect(self.DB_CLIENT)

            cursor = db.cursor()
            cursor.execute("""SELECT coin FROM client WHERE name = ?""", (name,))

            returned = cursor.fetchone()

            cursor.close()
            db.close()
            return returned[0]
        except sqlite3.OperationalError as e:
            print("[DB GET COIN ERROR]", e)
            pass


    def get_clients(self):
        db = sqlite3.connect(self.DB_CLIENT)

        cursor = db.cursor()
        cursor.execute('SELECT * FROM client')

        returned = cursor.fetchall()

        cursor.close()
        db.close()
        return returned

