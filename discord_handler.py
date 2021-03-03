from client import Client
import discord
from db import DataBase
import datetime
from timer import Timer
# ========================================== FIN DES IMPORTS ========================================================= #

"""
ex:

before : <VoiceState self_mute=True self_deaf=False self_stream=False channel=<VoiceChannel id=570728711268073686 name='Général' position=0 bitrate=64000 user_limit=0 category_id=570728711268073551>>
after : <VoiceState self_mute=True self_deaf=False self_stream=False channel=<VoiceChannel id=816070892752470086 name='hjk' position=1 bitrate=64000 user_limit=0 category_id=570728711268073551>>

"""

_COMMANDES = [
        {
            'name': "start_bet",
            'description': "demarre le bet"
        },

        {
            'name': "bet",
            'description': "parrie des coins"
        },

        {
            'name': "get_coins",
            'description': "affiche le nombre de coins quon a actuellement"
        },

        {
            'name': "correct",
            'description': "ferme le bet et paye les winnerz"
        },

        {
            'name': "is_started",
            'description': "affiche si un bet est lancé ou non"
        },

        {
            'name': "bet_help",
            'description': "affiche les commandes du bot"
        },
]


class DiscordHandler(discord.Client):

    _COIN_TO_ADD = 50

    client_handler = None

    REPONSE_1 = {"name": "oui", "emoticon": "👍"}
    REPONSE_2 = {"name": "non", "emoticon": "👎"}

    CORRECT_REPONSE = None

    BETS_LIST = []

    BET_IS_ALIVE = False

    BET_LOCK = False

    bet_utterance = None

    async def on_ready(self):
        db = DataBase()
        db.create()

        self.client_handler = ClientHandler()


        # envoi un message au salon test quand le bot est lancé
        # log_channel = self.get_channel(744957237319172167)
        # await log_channel.send('Logged in')
        print("[DISCORD INFO]", "bet can be started !")

        # chan = self.get_channel(816070892752470086)
        # voice_user = chan.members
        # print(voice_user)

        # self.loop.create_task(self.check_channel())



    async def on_voice_state_update(self, member, before, after):
        client = Client(str(member))
        client_name_id = client.name_id


        if before.channel is None and after.channel is not None:
            """ Nouvelle connexion à un channel """
            '''
                si before channel est None et after channel nest pas None c une nouvelle connexion
            '''
            self.client_handler.add_user(client)
            self.start_coin_service()
            print("[DISCORD INFO]", client_name_id, "connecter a un channel")



        if before.channel is not None and after.channel is not None:
            """ changement de channel on sen fou ducoup """
            '''
                si before channel nest pas None et after channel nest pas None c un changement de channel
            '''
            print("[DISCORD INFO]", client_name_id, "cest connecté a un autre channel")



        if before.self_deaf is False and before.self_deaf is True:
            """ client cest mute casque """
            pass



        if before.self_deaf is True and before.self_deaf is False:
            """ client cest demute casque """
            pass



        if before.channel is not None and after.channel is None:
            """ deconnexion d'un channel """
            '''
                si before channel nest pas None et after channel est None c une deconnexion de channel
                
                On arrete dadd les coin
            '''
            try:
                self.stop_coin_service()
                self.client_handler.remove_client(client.name_id)
                print("[DISCORD INFO]", client_name_id, "deconnecter dun channel")

            except Exception as e:
                print("[DISCORD DISCONNECT INFO]", e)

        # print("before :", before)
        # print("after :", after)

        # c = self.get_channel(570728711263879353)
        # self._IN_VOICE_CHANNEL_CLIENT.append(member)
        # await c.send("dsfsdf")



    async def on_reaction_add(self, reaction, user):
        """ envoie un message en dm quand on a recuperer le vote """
        if user != self.user:
            client = self.client_handler.get_client_from_name(str(user))
            if client is None:
                """ client non trouver dans la list des client connecter """
                await user.send('```tu dois etre connecter a un salon vocal pour parier```')

            else:

                if self.REPONSE_1['emoticon'] in str(reaction) or self.REPONSE_2['emoticon'] in str(reaction):

                    client.set_reponse(str(reaction))
                    user_coins_total = client.get_total_coins()

                    output_msg = "```"
                    output_msg += "Tu as voté " + client.get_reponse() + " au bet '" + self.bet_utterance + "'\n"
                    output_msg += "Tu as " + str(user_coins_total) + " coins\n\n"
                    output_msg += "Nombre de coin a parier :"
                    output_msg += "```"

                    await user.send(output_msg)



    async def on_message(self, message):
        if message.author == self.user:  # don't respond to ourselves
            return
        else:
            cmd = str(message.content)
            if cmd.startswith("!"):
                cmd = cmd.replace("!", "")

                if "bet_help" in cmd:
                    """ pour recuperer les commandes """

                    help_output = "```COMMANDES :\n"
                    for commande in _COMMANDES:
                        help_output += "\tcmd :  " + commande['name'] + "\n"
                        help_output += "\tdesc :  " + commande['description'] + "\n\n"
                    help_output += "```"
                    await message.channel.send(help_output)

                elif "start_bet" in cmd:
                    """ start le bet """

                    try:
                        utc_datetime = datetime.datetime.utcnow()
                        bet_time = utc_datetime.strftime("%d/%m/%Y à %H:%M:%S")

                        self.bet_utterance = cmd.replace("start_bet ", "")

                        embed_mess = discord.Embed(title=self.bet_utterance, description="Bet du " + bet_time)

                        embed_mess.add_field(name=self.REPONSE_1['name'], value=self.REPONSE_1['emoticon'])  # , inline=False)
                        embed_mess.add_field(name=self.REPONSE_2['name'], value=self.REPONSE_2['emoticon'])  # , inline=False)

                        output_bet = await message.channel.send(embed=embed_mess)

                        self.BET_IS_ALIVE = True

                        await output_bet.add_reaction(self.REPONSE_1['emoticon'])
                        await output_bet.add_reaction(self.REPONSE_2['emoticon'])

                    except Exception as e:
                        print("[DISCORD START BET INFO]", e)

                elif "bet" in cmd:
                    """ bet des coins """

                    try:
                        coin_to_bet = cmd.split(" ")[1]
                        client = self.client_handler.get_client_from_name(str(message.author))
                        if client is not None:
                            client_total_coins = client.get_total_coins()

                        if not self.BET_IS_ALIVE:
                            await message.channel.send("```Aucun bet n'est lancé```")

                        else:
                            if not client.have_bet:
                                """ si le client na pas deja bet il peu bet """

                                if int(client_total_coins) == 0:
                                    await message.channel.send("```Tu n'as pas de coins, dommage :///////////```")

                                elif int(coin_to_bet) > int(client_total_coins):
                                    await message.channel.send("```Tu n'as pas assez de coins, petit trou du culzzz```")

                                else:

                                    client.remove_coin(coin_to_bet)

                                    self.BETS_LIST.append((client.name_id, client.get_reponse(), coin_to_bet))

                                    output_msg = "```"
                                    output_msg += "Tu as bet " + str(coin_to_bet) + " coins"
                                    output_msg += "```"

                                    client.have_bet = True

                                    await message.channel.send(output_msg)

                            else:
                                output_msg = "```"
                                output_msg += "Tu as déja bet pour '" + self.bet_utterance + "'"
                                output_msg += "```"
                                await message.channel.send(output_msg)


                    except Exception as e:
                        print("[DISCORD BET INFO]", e)

                elif "get_coins" in cmd:
                    try:
                        client = self.client_handler.get_client_from_name(str(message.author))

                        output_msg = "```"
                        output_msg += "Tu as " + str(client.get_total_coins()) + " coins"
                        output_msg += "```"

                        await message.channel.send(output_msg)

                    except Exception as e:
                        print("[DISCORD GET COINS INFO]", e)

                elif "correct" in cmd:

                    if self.BET_IS_ALIVE is False:
                        await message.channel.send("```Aucun bet n'est lancé```")

                    else:
                        maybe_correct = cmd.replace("correct ", "").lower()
                        if maybe_correct == self.REPONSE_1['name'] or maybe_correct == self.REPONSE_1['emoticon']:
                            self.CORRECT_REPONSE = self.REPONSE_1['emoticon']

                        elif maybe_correct == self.REPONSE_2['name'] or maybe_correct == self.REPONSE_2['emoticon']:
                            self.CORRECT_REPONSE = self.REPONSE_2['emoticon']

                        else:
                            rep_output = "```"
                            rep_output += "La réponse entré ne correspond pas petit dogzz"
                            rep_output += "```"

                            await message.channel.send(rep_output)



                        if self.CORRECT_REPONSE is not None:

                            # calcul le total des coins parié
                            total_all_coins = sum(int(x[2]) for x in self.BETS_LIST)

                            # calcul des coins total des votant gagnant
                            winner_total_coins = sum(int(x[2]) for x in self.BETS_LIST if x[1] == self.CORRECT_REPONSE)

                            # on add les coins a tout les winners
                            # en fonction de se qui ont voté
                            winners = []
                            for client in self.BETS_LIST:
                                bet_client_name = client[0]
                                bet_client_voted_for = client[1]
                                bet_client_voted_coins = client[2]

                                client = self.client_handler.get_client_from_name(bet_client_name)

                                if bet_client_voted_for == self.CORRECT_REPONSE:

                                    payout = int(total_all_coins * int(bet_client_voted_coins) / winner_total_coins)
                                    client.add_coin(payout)

                                    winners.append("" + str(client.name_id + " à gagné " + str(payout) + " coins") + "\n")

                            rep_output = "```"
                            for winner in winners:
                                rep_output += winner
                            rep_output += "```"

                            if rep_output == "``````":
                                await message.channel.send("```ahahah aucun gagnant les dogitos```")
                            else:
                                await message.channel.send(rep_output)

                            self.BET_LOCK = False
                            self.BET_IS_ALIVE = False
                            winners.clear()

                elif "is_started" in cmd:
                    if self.BET_IS_ALIVE:
                        output_msg = "```"
                        output_msg += "Le bet '" + self.bet_utterance + "' est lancé"
                        output_msg += "```"
                        await message.channel.send(output_msg)

                    else:
                        output_msg = "```"
                        output_msg += "Aucun bet lancé"
                        output_msg += "```"
                        await message.channel.send(output_msg)

            else:
                pass



    def start_coin_service(self):
        """ start adding coin to user in voice channels """
        try:
            for client in self.client_handler.get_all_users():
                if client.is_adding_coin:
                    pass    # client ajoute deja des coins inutile de le relancer
                else:
                    client.start_adding_coins(self._COIN_TO_ADD)
                    # print("starting adding coin for", client.name_id)
        except Exception as e:
            print("[DISCORD INFO]", e)



    def stop_coin_service(self):
        """ stop adding coin to user in voice channels """
        try:
            for client in self.client_handler.get_all_users():
                if client.is_adding_coin:
                    client.stop_adding_coin()
                    # print("stoping adding coin for", client.name_id)
                else:
                    pass    # client a arreter dajouter des coins inutile de le relancer
        except Exception as e:
            print("[DISCORD INFO]", e)



class ClientHandler:
    _CLIENT_LIST = []

    def add_user(self, user: Client):
        self._CLIENT_LIST.append(user)

    def get_client_from_name(self, name: str):
        for client in self._CLIENT_LIST:
            if client.name_id in name:
                return client

    def get_all_users(self):
        return self._CLIENT_LIST

    def remove_client(self, name: str):
        for client in self._CLIENT_LIST:
            if client.name_id in name:
                self._CLIENT_LIST.remove(client)
                break






