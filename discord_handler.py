from client_handler import ClientHandler
from client import Client
from bet_handler import BetHandler
from bet import Bet, ClientBet
import datetime
import time
import discord
import asyncio
from db import DataBase
from tuto import _tuto_
from classement import Classement
from threading import Thread
# ========================================== FIN DES IMPORTS ========================================================= #

__version__ = "alpha 0.3.1"

__saison__ = "saison 2"

_COMMANDES_ = {'cmd': [{
                'start': "start_bet",
                'description': "demarre le bet  | (ex: !start_bet <phrase>, <reponse1>/<reponse2>)"
            },

            {
                'stop': "stop_bet",
                'description': "stop le bet  | (ex: !stop_bet <reponse correct>)"
            },

            {
                'pause': "pause_bet",
                'description': "pause le bet pour que plus personne puisse bet  | (ex: !pause_bet)"
            },

            {
                'bet': "bet",
                'description': "parrie des coins  | (ex: !bet <nb de coin a bet> ou !bet <nb de coin a bet> <nom de lowner pour repondre a son bet>)"
            },

            {
                'help': "help_bet",
                'description': "affiche les commandes du bot"
            },

            {
                'running': "get_bets",
                'description': "affiche les bets en cours  | (ex: !stop_bet <reponse correct>)"
            },

            {
                'coins': "get_coins",
                'description': "affiche le nombre de coins quon a actuellement  | (ex: !get_coins)"
            },

            {
                'cancel': "cancel_bet",
                'description': "cancel le bet pour celui qui la demander  | (ex: !cancel_bet)"
            },

            {
                'coin_flip': "coin_flip",
                'description': "pile ou face  | (ex: !coin_flip)"
            },

            {
                'tuto': "tuto",
                'description': "affiche le tuto"
            },

            {
                'classement': "classement",
                'description': "affiche le classement"
            },

            {
                'version': "version",
                'description': "affiche la version"
            },

            {
                'report': "report",
                'description': "report un bug ou une requete (50 requetes max en tout autorisé)"
            },
]}





class DiscordHandler(discord.Client):
    _DB = DataBase()

    _COIN_TO_ADD = 3
    _TIME_BEFORE_ADDING_COIN = 1800  # 30 minutes
    _CHANNEL_TO_EXCLUDE = 465336735702974464    # salon afk


    client_handler = None
    bet_handler = None


    def __init__(self, **options):
        intents = discord.Intents.all()     # pour recup tous les users
        super().__init__(**options, intents=intents)
        self.intents.members = True     # pour recup tous les users



    async def on_ready(self):
        self._DB.create()

        self.client_handler = ClientHandler()
        self.bet_handler = BetHandler()


        print("[DISCORD INFO]", "Listing des users ...")
        await self.change_presence(activity=discord.Game(name="Listé les users"))

        for guild in self.guilds:
            for member in guild.members:
                #        Client(name       , uuid)
                client = Client(str(member), str(member.id))
                self.client_handler.add_user(client)


        # === FIN DE L'INIT DU BOT
        #
        print("[DISCORD INFO]", "bet can be started !")
        await self.change_presence(activity=discord.Game(name="version : " + str(__version__)))
        # await self.change_presence(activity=discord.Game(name="recevoir vos bets"))
        # ===


    async def on_member_join(self, member):
        #        Client(name       , uuid)
        client = Client(str(member), str(member.id))
        self.client_handler.add_user(client)


    async def on_reaction_add(self, reaction, user):
        """ envoie un message en dm quand on a recuperer le vote """
        if user != self.user:

            client_exist = self._DB.get_if_clien_exist(str(user))

            if client_exist is None:
                """ client non trouver dans la list des client connecter """
                await user.send('```tu dois te connecter au moins une fois a un vocal pour tenregistrer```')

            else:
                bet_id = str(reaction.message.id)
                bet = self.bet_handler.get_bet_from_uuid(bet_id)


                if bet is not None:

                    if not bet.is_locked():

                        client = self.client_handler.get_client_from_name(str(user))

                        rep_1 = bet.get_reponse_1()
                        rep_2 = bet.get_reponse_2()

                        if str(reaction) == rep_1['emoticon']:
                            rep = rep_1['emoticon']

                        elif str(reaction) == rep_2['emoticon']:
                            rep = rep_2['emoticon']

                        else:
                            rep = "None"

                        if rep:
                            client.set_reponse(str(rep))


                        if rep_1['emoticon'] in str(reaction) or rep_2['emoticon'] in str(reaction):
                            user_coins_total = client.get_total_coins()

                            output_msg = "```"
                            output_msg += "Tu as voté " + str(rep) + " au bet '" + str(bet.get_utterance()) + "'\n"
                            output_msg += "Tu as " + str(user_coins_total) + " coins\n\n"
                            output_msg += "Nombre de coin a parier :\n"
                            output_msg += "Exemple : '!bet 50' ou '!bet 50 name#0000' pour parrier sur le bet de quelquun en particulier"
                            output_msg += "```"
                            client.have_bet = True

                            await user.send(output_msg)

                    else:
                        output_msg = "``` le bet ne peut plus recevoir de parri ```"
                        await user.send(output_msg)

                else:
                    """ ce nest pas un bet """
                    pass



    async def on_voice_state_update(self, member, before, after):


            try:
                if int(after.channel.id) == int(self._CHANNEL_TO_EXCLUDE):
                    """ salon afk """
                    print("[DISCORD INFO]", str(member), "connecter au channel AFK")

                    # client = self.client_handler.get_client_from_name(str(member))

                    # if client is not None:
                    #     client.is_deaf_in_vocal = True
            except AttributeError:
                # client deco du channel donc plus d'id
                pass



            if before.channel is None and after.channel is not None:
                """ Nouvelle connexion à un channel """
                '''
                    si before channel est None et after channel nest pas None c une nouvelle connexion
                '''
                print("[DISCORD INFO]", str(member), "connecter a un channel")

                # if before.self_deaf is not True:

                #     client = self.client_handler.get_client_from_name(str(member))

                #     if client is not None:
                #         client.is_connected_in_vocal = True
                #         self.loop.create_task(self.client_service_add_coins(client))



            if before.self_deaf is True and before.channel is None and after.channel is not None:
                """ Nouvelle connexion à un channel en etant mute casque """
                print("[DISCORD INFO]", str(member), "connecté en etant mute a un channel")

                # client = self.client_handler.get_client_from_name(str(member))

                # if client is not None:
                #     client.is_deaf_in_vocal = True
                #     client.is_connected_in_vocal = True
                #     self.loop.create_task(self.client_service_add_coins(client))



            if before.self_deaf is False and after.self_deaf is True:
                """ client cest mute casque """
                print("[DISCORD INFO]", str(member), "mute dun channel")

                # client = self.client_handler.get_client_from_name(str(member))

                # if client is not None:
                #     client.is_deaf_in_vocal = True



            if before.self_deaf is True and after.self_deaf is False:
                """ client cest demute casque """
                print("[DISCORD INFO]", str(member), "demute dun channel")

                # client = self.client_handler.get_client_from_name(str(member))

                # if client is not None:
                #     client.is_deaf_in_vocal = False



            if before.channel is not None and after.channel is None:
                """ deconnexion d'un channel """
                '''
                    si before channel nest pas None et after channel est None c une deconnexion de channel
        
                    On arrete dadd les coin
                '''
                print("[DISCORD INFO]", str(member), "deconnecter dun channel")

                # client = self.client_handler.get_client_from_name(str(member))

                # if client is not None:
                #     client.is_connected_in_vocal = False
                #     client.is_deaf_in_vocal = False


    async def on_message(self, message):

        _cmd_ = _COMMANDES_['cmd']

        if message.author == self.user:  # don't respond to ourselves
            return

        else:
            user_input = str(message.content)

            if "  " in user_input:
                user_input = user_input.replace("  ", " ")


            if user_input.startswith("!"):
                user_input = user_input.replace("!", "")    # peut remplacer les '!' si yen a dautre


                if len(user_input.split(" ")) == 1:
                    # si il y a juste la commande sans rien en plus
                    user_cmd = user_input.replace("!", "")
                else:
                    user_cmd = user_input.split(" ")[0].replace("!", "")


                channel = message.channel


                ####################################
                #   traitement des commandes
                #
                for cmd in _cmd_:

                    try:
                        if cmd['bet'] == user_cmd:
                            """ bet des coins """
                            if len(user_input.split(' ')) > 1:  # si il y a que la commandes sans les coins a bet
                                user = str(message.author)
                                user_input = user_input.replace(user_cmd + " ", "")
                                await self.cmd_bet(user_input, user, channel=channel)

                            else:
                                await channel.send("``` il manque les coins a bet ```")
                    except:
                        pass


                    try:
                        if cmd['help'] == user_cmd:
                            """ pour recuperer les commandes """
                            await self.cmd_help(channel=channel)
                    except:
                        pass


                    try:
                        if cmd['start'] == user_cmd:
                            """ start le bet """
                            bet_owner = message.author
                            user_input = user_input.replace(user_cmd + " ", "")
                            await self.cmd_start_bet(user_input, bet_owner, channel=channel)
                    except:
                        pass


                    try:
                        if cmd['pause'] == user_cmd:
                            """ start le bet """
                            bet_owner = message.author
                            await self.cmd_pause_bet(bet_owner, channel=channel)
                    except:
                        pass


                    try:
                        if cmd['stop'] == user_cmd:
                            """ start le bet """
                            bet_owner = message.author
                            user_input = user_input.replace(user_cmd + " ", "")
                            await self.cmd_stop_bet(user_input, bet_owner, channel=channel)
                    except:
                        pass


                    try:
                        if cmd['running'] == user_cmd:
                            await self.cmd_get_bets(channel=channel)
                    except:
                        pass


                    try:
                        if cmd['coins'] == user_cmd:
                            user = str(message.author)
                            await self.cmd_get_coins(channel=channel, user=user)
                    except:
                        pass


                    try:
                        if cmd['cancel'] == user_cmd:
                            bet_owner = message.author
                            await self.cmd_cancel_bet(bet_owner, channel=channel)
                    except:
                        pass


                    try:
                        if cmd['coin_flip'] == user_cmd:
                            await self.cmd_coin_flip(channel=channel)
                    except:
                        pass


                    try:
                        if cmd['tuto'] == user_cmd:
                            await self.cmd_tuto(channel=channel)
                    except:
                        pass


                    try:
                        if cmd['classement'] == user_cmd:
                            await self.cmd_get_classement(channel=channel)
                    except:
                        pass


                    try:
                        if cmd['version'] == user_cmd:
                            await self.cmd_get_version(channel=channel)
                    except:
                        pass


                    try:
                        if cmd['report'] == user_cmd:
                            owner = str(message.author)
                            user_input = user_input.replace(user_cmd + " ", "")
                            await self.cmd_report(user_input, owner, channel=channel)
                    except:
                        pass


                ####################################
                #   COMMANDE POUR ADMIN UN PEU
                #
                if str(message.author) == "sɐɯoɥ⊥#4897":
                    try:
                        add_cmd = "add_coins"
                        if add_cmd == user_cmd:
                            user_input = user_input.replace(add_cmd + " ", "")
                            await self.admin_add_coins(user_input, channel=channel)
                    except:
                        pass

                    try:
                        rm_cmd = "rm_coins"
                        if rm_cmd == user_cmd:
                            user_input = user_input.replace(rm_cmd + " ", "")
                            await self.admin_rm_coins(user_input, channel=channel)
                    except:
                        pass

                    try:
                        set_cmd = "set_coins"
                        if set_cmd == user_cmd:
                            user_input = user_input.replace(set_cmd + " ", "")
                            await self.admin_set_coins(user_input, channel=channel)
                    except:
                        pass



            else:
                ####################################
                #       other user input
                print("[OTHER MESSAGE] " + str(message.author) + " à écrit : " + str(user_input))
                pass





    # ============================ FONCTIONS DES COMMANDES =============================== #


    async def client_bet_update_quote(self, bet, msg_output_bet, bet_utterance, bet_time, rep1, rep2, owner):
        c = 0
        while True:
            if bet.get_utterance() is not None:
                # do something
                embed_mess = discord.Embed(title=bet_utterance, description="Bet du " + bet_time)
                embed_mess.add_field(name="owner", value=owner, inline=False)
                embed_mess.add_field(name=rep1['name'], value=rep1['emoticon'] + "\n" + str(bet.get_cote()[0]))
                embed_mess.add_field(name=rep2['name'], value=rep2['emoticon'] + "\n" + str(bet.get_cote()[1]))

                await msg_output_bet.edit(embed=embed_mess)
                await asyncio.sleep(2)
                c += 1

            else:
                break



    async def client_service_add_coins(self, client):
        pass
        # while True:

        #     if client.is_deaf_in_vocal:
        #         print("[SERVICE ADDING COINS]", "waiting for", client.name_id, "to demute headset")
        #         await asyncio.sleep(2)
        #         pass

        #     elif client.is_connected_in_vocal:
        #         # do something
        #         await asyncio.sleep(self._TIME_BEFORE_ADDING_COIN)
        #         print("[SERVICE ADDING COINS]", "adding", self._COIN_TO_ADD, "coins to", client.name_id)
        #         client.add_coin(self._COIN_TO_ADD)

        #     else:
        #         print("[SERVICE ADDING COINS]", "stop service for", client.name_id, "- (cause : déconnexion)")
        #         break



    async def cmd_get_version(self, channel):
        """ affiche la version actuelle """
        await channel.send("```Version : " + str(__version__) + "```")



    async def cmd_report(self, user_input: str, owner: str, channel):
        """ commande pour report un truc """
        import os


        if "report" not in user_input:
            report_path = os.path.join(os.getcwd(), "report")
            report_file_count = len([name for name in os.listdir(report_path) if os.path.isfile(os.path.join(report_path, name))])

            if not os.path.exists(report_path):
                os.mkdir(report_path)

            if int(report_file_count) <= 50:

                _report_datetime = datetime.datetime.utcnow()
                report_datetime = _report_datetime.strftime("%d-%m-%Y_%H-%M-%S")

                with open(os.path.join(report_path, "_" + str(owner) + report_datetime +".txt"), "w+") as report_file:
                    report_file.write(user_input)
                    report_file.close()

                await channel.send("```Un report a été envoyé```")

            else:
                await channel.send("```Il y a trop de report pour le moment```")


        else:
            await channel.send("```Il faut du text pour votre report```")



    async def cmd_bet(self, user_input: str, user: str, channel):
        """ permet de bet des coins   ex: si '1' a lancer un bet seul lui peu le stop """
        all_bet = self.bet_handler.get_all_bets()

        if len(all_bet) >= 1:

            splitted_user_input = user_input.split(" ")

            client = self.client_handler.get_client_from_name(str(user))
            client_reponse = client.get_reponse()


            # check si luser a repondu ou non avec les reactions
            if client_reponse != "None":

                if "all in" in user_input:
                    coin_to_bet = client.get_total_coins()
                    bet = all_bet[-1:][0]  # le dernier bet enregistrer

                    client.remove_coin(coin_to_bet)
                    bet.do_bet(ClientBet(str(client.name_id), str(client_reponse), str(coin_to_bet)))

                    await channel.send("```" + str(client.name_id) + " tu as voté " + str(coin_to_bet) + " coins sur '" + str(client_reponse) + "' de '" + str(bet.get_utterance()) + "'```")


                elif len(splitted_user_input) == 1:   # bet sur le dernier bet enregistrer

                    find_nb_coins_bet = [int(s) for s in user_input.split() if s.isdigit()]

                    if len(find_nb_coins_bet) > 0:
                        coin_to_bet = find_nb_coins_bet[0]

                        # check si luser a asser de coins
                        if int(client.get_total_coins()) == 0:
                            await channel.send("```" + client.name_id + " tu nas plus de coins ```")

                        elif int(coin_to_bet) == 0:
                            await channel.send("```" + client.name_id + " tu ne peut pas voté 0 coins ```")

                        elif int(coin_to_bet) > int(client.get_total_coins()):
                            await channel.send("```" + client.name_id + " tu nas pas assez coins ```")

                        else:
                            bet = all_bet[-1:][0]  # le dernier bet enregistrer

                            client.remove_coin(coin_to_bet)
                            bet.do_bet(ClientBet(str(client.name_id), str(client_reponse), str(coin_to_bet)))

                            await channel.send("```" + str(client.name_id) + " tu as voté " + str(coin_to_bet) + " coins sur '" + str(client_reponse) + "' de '" + str(bet.get_utterance()) + "'```")

                    else:
                        await channel.send("```nombre de coin a bet non trouvé```")



                elif len(splitted_user_input) == 2:  # bet sur le bet du owner defini

                    user_to_add_coin_on_his_bet = splitted_user_input[1]

                    find_nb_coins_bet = [int(s) for s in user_input.split() if s.isdigit()]

                    if len(find_nb_coins_bet) > 0:
                        coin_to_bet = find_nb_coins_bet[0]

                        # check si luser a asser de coins
                        if int(client.get_total_coins()) == 0:
                            await channel.send("```" + client.name_id + " tu nas plus de coins ```")

                        elif int(coin_to_bet) > int(client.get_total_coins()):
                            await channel.send("```" + client.name_id + " tu nas pas assez coins ```")

                        else:
                            bet = self.bet_handler.get_bet_from_owner(user_to_add_coin_on_his_bet)

                            client.remove_coin(coin_to_bet)
                            bet.do_bet(ClientBet(str(client.name_id), str(client_reponse), str(coin_to_bet)))

                            await channel.send("```" + str(client.name_id) + " tu as voté " + str(coin_to_bet) + " coins sur '" + str(client_reponse) + "' de '" + str(bet.get_utterance()) + "'```")

                    else:
                        await channel.send("```nombre de coin a bet non trouvé```")

            else:
                await channel.send("```il faut repondre a un bet avec une reaction pour bet tes coins trou du cuuuuuuuullllzzzz```")

        else:
            await channel.send("```Aucun bet n'est lancé```")



    async def cmd_stop_bet(self, user_input: str, owner: str, channel):
        """ stop le bet par user   ex: si '1' a lancer un bet seul lui peu le stop """
        bet = self.bet_handler.get_bet_from_owner(str(owner))

        if bet is not None:  # si il a un bet a lui qui existe

            output = "```"

            if "stop_bet" != user_input:
                correct_reponse = user_input


                if correct_reponse in bet.get_reponse_1()['name'] or correct_reponse == bet.get_reponse_1()['emoticon']:
                    bet.set_correct_reponse(str(correct_reponse))


                elif correct_reponse in bet.get_reponse_2()['name'] or correct_reponse == bet.get_reponse_2()['emoticon']:
                    bet.set_correct_reponse(str(correct_reponse))

                else:
                    await channel.send("```la reponse donné ne correspond à aucunes du bet```")
                    return


                # calcul les gains
                payout_list = bet.calcul_payout()

                winners = bet.get_winners()
                loosers = bet.get_loosers()


                output += "La bonne réponse au bet '" + str(bet.get_utterance()) + "' était '" + str(bet.get_correct_reponse()) + "'\n"



                if len(winners) == 0 and len(loosers) == 0:
                    output += "\n"
                    output += "\tPersonne n'a voté"

                elif len(winners) == 0 and len(loosers) != 0:
                    output += "\n"
                    output += "\tAucun gagnants les dogs 🥵\n\n"

                    for client_bet in bet.get_bet_list():  # on redonne les coins a ce qui les ont bets
                        client_name = client_bet.name
                        client_payback = client_bet.nb_coins

                        client = self.client_handler.get_client_from_name(client_name)
                        client.add_coin(client_payback)
                        output += "\t" + str(client_name) + " a récupéré ces " + str(client_payback) + " coins\n"


                else:

                    if len(winners) != 0:
                        output += "\n"

                        for payout_winner in payout_list:
                            client_win = payout_winner[0]
                            payout = payout_winner[1]

                            client = self.client_handler.get_client_from_name(str(client_win))
                            client.add_coin(int(payout))
                            output += "\t" + str(client_win) + " à voté '" + str(bet.get_correct_reponse()) + "' et a gagné " + str(payout) + " coins\n"



                    if len(loosers) != 0:
                        output += "\n"

                        for looser in loosers:
                            client_name = looser[0]
                            client_reponse = looser[1]
                            client_coins_voted = looser[2]

                            output += "\t" + str(client_name) + " à voté '" + str(client_reponse) + "' et a perdu " + str(client_coins_voted) + " coins\n"




                for player in bet.player_names_of_the_bet():
                    client = self.client_handler.get_client_from_name(str(player))
                    client.reset_bet()


                uuid = str(bet.get_uuid())
                bet.stop()
                self.bet_handler.remove_bet(uuid)

            else:
                output += "!stop_bet a besoin de la reponse juste pour cloturer le bet"

            output += "```"

            await channel.send(str(output))



    async def cmd_pause_bet(self, owner: str, channel):
        """ pause le bet par user   ex: si '1' a lancer un bet seul lui peu le pause """
        bet = self.bet_handler.get_bet_from_owner(str(owner))

        if str(bet.get_owner()) == str(owner):  # si il a un bet a lui qui existe
            bet.lock()

            output = "```"
            output += "le bet de " + str(bet.get_owner()) + " ne peut plus recevoir de bets"
            output += "```"

            await channel.send(output)



    async def cmd_start_bet(self, user_input: str, owner: str, channel):
        """ lance un bet (un seul bet par utilisateur a la fois) """

        owner_have_already_a_bet = self.bet_handler.get_bet_from_owner(str(owner))

        if owner_have_already_a_bet is None:  # si il na pas deja de bet il peu en commencé un

            bet = Bet(user_input)
            bet.set_owner(owner)

            bet_time = bet.get_bet_date()
            bet_utterance = bet.get_utterance()
            rep1 = bet.get_reponse_1()
            rep2 = bet.get_reponse_2()
            owner = bet.get_owner()


            self.bet_handler.add_bet(bet)


            embed_mess = discord.Embed(title=bet_utterance, description="Bet du " + bet_time)


            embed_mess.add_field(name="owner",
                                 value=owner,
                                 inline=False)

            embed_mess.add_field(name=rep1['name'],
                                 value=rep1['emoticon'])

            embed_mess.add_field(name=rep2['name'],
                                 value=rep2['emoticon'])


            msg_output_bet = await channel.send(embed=embed_mess)

            _bet_uuid = msg_output_bet.id
            bet.set_uuid(_bet_uuid)

            # testing
            self.loop.create_task(self.client_bet_update_quote(bet, msg_output_bet, bet_utterance, bet_time, rep1, rep2, owner))

            await msg_output_bet.add_reaction(rep1['emoticon'])
            await msg_output_bet.add_reaction(rep2['emoticon'])

        else:
            await channel.send("```" + str(owner) + " tu as déjà un bet en cour```")



    async def cmd_cancel_bet(self, owner: str, channel):
        bet = self.bet_handler.get_bet_from_owner(str(owner))

        if bet is not None:

            for client_bet in bet.get_bet_list():   # on redonne les coins a ce qui les ont bets
                client_name = client_bet.name
                client_payback = client_bet.nb_coins

                client = self.client_handler.get_client_from_name(client_name)
                client.add_coin(client_payback)

            output = "```" + str(owner) + " cancel du bet '" + str(bet.get_utterance()) + "'```"

            bet.stop()
            self.bet_handler.remove_bet(str(bet.get_uuid()))

            await channel.send(output)



    async def cmd_get_coins(self, user: str, channel):
        client = self._DB.get_if_clien_exist(str(user))

        client_coins = self._DB.get_coins_from_name(str(user))

        output_msg = "```"
        output_msg += "" + str(client) + " tu as " + str(client_coins) + " coins"
        output_msg += "```"

        await channel.send(output_msg)



    async def cmd_get_bets(self, channel):
        bets = self.bet_handler.get_all_bets()

        output = "```BETS en cours :\n\n"
        if len(bets) >= 1:
            for bet in bets:

                ut = bet.get_utterance()
                rep_1 = bet.get_reponse_1()
                rep_2 = bet.get_reponse_2()

                id = str(bet.get_id())

                owner = str(bet.get_owner())
                date = str(bet.get_bet_date())
                # uuid = str(bet.get_uuid())

                output += "\tBet#" + str(id) + " : " + str(ut) + "\n"
                output += "\t\towner : " + str(owner) + "\n"
                output += "\t\treponses : " + str(rep_1['name']) + ", " + str(rep_2['name']) + "\n"
                output += "\t\tdate : " + str(date) + "\n"
                # output += "\t\tuuid : " + uuid + "\n"


        else:
            output += "\tAucun bet yazeubi"

        output += "```"
        await channel.send(output)



    async def cmd_help(self, channel):
        help_output = "```COMMANDES :\n"
        for cmd in _COMMANDES_['cmd']:
            name = str(cmd).split("': '")[0].replace("{'", "")

            help_output += "\tcmd :  " + str(cmd[name]) + "\n"
            help_output += "\tdesc :  " + str(cmd['description']) + "\n\n"

        help_output += "```"

        await channel.send(help_output)



    async def cmd_coin_flip(self, channel):
        import random
        coin = ["pile", "face"]
        await channel.send('```' + str(random.choice(coin)) + '```')


    async def cmd_tuto(self, channel):
        import os
        with open("tuto.txt", "w") as file:
            file.write(_tuto_)
            file.close()

        with open("tuto.txt", "rb") as file:
            await channel.send("Le tuto du bot bet : ", file=discord.File(file, "tuto.txt"))

        os.remove("tuto.txt")


    async def cmd_get_classement(self, channel):
        _classement = Classement()
        classement = _classement.get_classement()

        c = 1

        output_msg = "```"
        output_msg += "[CLASSEMENT]" + "\n\n"

        if classement:  # si ya du monde dans la db

            for classed in classement:
                if c <= 20:
                    if str(classed).startswith("1#"):
                        output_msg += "🧞 " + str(classed) + "\n"
                    else:
                        output_msg += classed + "\n"

                c += 1

            output_msg += "\n💩 " + str(_classement.last) + "\n\n\n"

        else:
            output_msg += "okamari no suzoki saskue-chan"

        output_msg += "```"
        await channel.send(output_msg)




    # ============================ FONCTIONS ADMINS =============================== #


    async def admin_set_coins(self, user_input: str, channel):
        input_splitted = user_input.split(" ")
        client_name = input_splitted[0]
        coin_to_add = input_splitted[1]

        client = self.client_handler.get_client_from_name(client_name)
        if client is not None:
            client.set_coin(int(coin_to_add))
            await channel.send('```' + str(coin_to_add) + ' coins mis a ' + str(client_name) + '```')
        else:
            await channel.send('```' + str(client_name) + ' non trouvé```')


    async def admin_add_coins(self, user_input: str, channel):
        input_splitted = user_input.split(" ")
        client_name = input_splitted[0]
        coin_to_add = input_splitted[1]

        client = self.client_handler.get_client_from_name(client_name)
        if client is not None:
            client.add_coin(int(coin_to_add))
            await channel.send('```' + str(coin_to_add) + ' coins ajouté a ' + str(client_name) + '```')
        else:
            await channel.send('```' + str(client_name) + ' non trouvé```')


    async def admin_rm_coins(self, user_input: str, channel):
        input_splitted = user_input.split(" ")
        client_name = input_splitted[0]
        coin_to_rm = input_splitted[1]

        client = self.client_handler.get_client_from_name(client_name)
        if client is not None:
            client.remove_coin(int(coin_to_rm))
            await channel.send('```' + str(coin_to_rm) + ' coins enlevé a ' + str(client_name) + '```')
        else:
            await channel.send('```' + str(client_name) + ' non trouvé```')



