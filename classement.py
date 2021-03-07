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

            if c_coins == 1000:
                """ si une personne est a 1000 cest quil a jamais bet"""
                pass
            else:
                self._classement_by_desc.append(str(classment_int) + "# " + str(c_name) + " avec " + str(c_coins) + " coins")
                if not self.first:
                    self.first = c_name
                elif not self.second:
                    self.second = c_name
                elif not self.third:
                    self.third = c_name
                else:
                    pass
                classment_int += 1

        self.last = c_name

