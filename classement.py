from db import DataBase
# ========================================== FIN DES IMPORTS ========================================================= #


class Classement:
    _db = DataBase()

    first = False
    second = False
    third = False
    last = False


    def __init__(self):
        self._classement_by_desc = []

        self.clients_list = self._db.sort_by_desc()

        if self.clients_list is not None:
            self.classifier()

    def get_classement(self):
        return self._classement_by_desc

    def classifier(self):
        classment_int = 1
        for c in self.clients_list:
            c_name = c[0]
            c_coins = c[1]

            if c_coins == 300:
                """ si une personne est a 300 cest quil a jamais bet"""
                pass
            else:
                self._classement_by_desc.append(str(classment_int) + "# " + str(c_name) + " avec " + str(c_coins) + " coins")
                if not self.first:
                    self.first = str(c_name) + " avec " + str(c_coins) + " coins"
                elif not self.second:
                    self.second = str(c_name) + " avec " + str(c_coins) + " coins"
                elif not self.third:
                    self.third = str(c_name) + " avec " + str(c_coins) + " coins"
                else:
                    pass
                classment_int += 1

                self.last = str(classment_int) + "# " + str(c_name) + " avec " + str(c_coins) + " coins"

