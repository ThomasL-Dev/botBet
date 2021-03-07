from client import Client
# ========================================== FIN DES IMPORTS ========================================================= #



class ClientHandler:
    _CLIENT_LIST = []


    def add_user(self, user: Client):
        self._CLIENT_LIST.append(user)


    def get_client_from_name(self, name: str):
        for client in self._CLIENT_LIST:
            if client.name_id in name:
                return client

        # find by number atfer the '#'
        # if special char in user name
        for client in self._CLIENT_LIST:
            hash_number_from_input = str(name).split("#")[1]
            hash_number_from_client = str(client.name_id).split("#")[1]

            if int(hash_number_from_input) == int(hash_number_from_client):
                return client


    def get_all_users(self):
        return self._CLIENT_LIST


    def remove_client(self, name: str):
        for client in self._CLIENT_LIST:
            if client.name_id in name:
                self._CLIENT_LIST.remove(client)
                break
