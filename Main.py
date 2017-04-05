from pymongo import MongoClient
from time import *
import requests
import json

import Users
import Telegram
import Games

# configuration

print("connecting to mongodb")
client = MongoClient()
client = MongoClient('localhost', 27017)
print("connected  to mongodb")

database = client.LongMan
playersCollection = database.players
gamesCollection = database.games
chatStatus = database.chatStatus

Users.playersCollection = database.players
Users.gamesCollection = database.games
Telegram.gamesCollection = database.games
Telegram.chatStatus = database.chatStatus

Games.playersCollection = database.players
Games.gamesCollection = database.games
Games.chatStatus = database.chatStatus


# general funcotion
def start_command(playerId):
    if Users.checkPlayerId(playerId):
        Telegram.sendMessage(playerId, 'wellcome back dude :D')
        return False
    else:
        for status in chatStatus.find({'pid' : playerId}):
            return False

        Telegram.sendMessage(playerId, 'wellcome to game, enter your name')
        chatStatus.insert({'pid': playerId, 'value' : 'REGISTER'})
        return True

def create_command(playerId):
    for game in gamesCollection.find({'status' : 'WAITING', 'players._id' : playerId}):
        Telegram.sendMessage(playerId, 'you are still in a game please quit it by using /cancel to restart')
        return False

    Telegram.sendMessage(playerId, 'how much do you wanna to bet?(max: ' + str(Users.getScore(playerId)) + ')')
    chatStatus.insert({'pid': playerId, 'value' : 'CREATE'})
    return True

def cancel_command(playerId):
    for game in gamesCollection.find({'status' : 'WAITING', 'creator._id' : playerId}):
        keyboard = {
                    "keyboard": [[
                                    {"text": "yes"},{"text": "no"}
                                ]] 
                    }

        message = 'do you cancel this game? there are ' + str(len(game['players'])) + ' players in game'
        Telegram.sendMessage(playerId, message, keyboard)

        for status in chatStatus.find({'pid' : playerId}):
            if status['value'] == 'CANCEL_WAITING_GAME':
                return True
        
        chatStatus.insert({'pid': playerId, 'value' : 'CANCEL_WAITING_GAME'})
        return True

    for game in gamesCollection.find({'status' : 'PLAYING', 'players._id' : playerId}):
        keyboard = {
                    "keyboard": [[
                                    {
                                        "text": "yes"
                                    },
                                    {
                                        "text": "no"
                                    }
                                ]] 
                    }
        message = 'are you sure to quit this game? if you quite you\'ll loss ' + str(game['bet'])
        Telegram.sendMessage(playerId, message, keyboard)

        chatStatus.insert({'pid': playerId, 'value' : 'CANCEL_PLAYING_GAME', 'game' : game})
        return True

def messageRecieved(playerId, message):
    if message == '/start':
        print(str(playerId) + "started bot")
        start_command(playerId)
    
    elif message == '/create':
        print(str(playerId) + " wanna start a new game")
        create_command(playerId)

    elif message == '/cancel':
        print(str(playerId) + " wanna cencel game")
        cancel_command(playerId)

    elif message.startswith("/join"):
        parts = message.split(" ")
        if len(parts) == 1:
            pass
        elif len(parts) == 2:
            gameId = int(parts[1])

    else:
        for status in chatStatus.find({'pid' : playerId}):
            # register
            if status['value'] == 'REGISTER':
                print("player " + str(playerId) + "registered")
                if register(playerId, message, playersCollection):
                    chatStatus.delete_many({'_id' : playerId})

            # create
            elif status['value'] == 'CREATE':
                maxBet = Users.getScore(playerId)
                if int(message) > maxBet:
                    Telegram.sendMessage(playerId, 'you don\'t have enough score to bet, enter again?(max: ' + str(Users.getScore(playerId)) + ')')
                else:
                    Games.createGame(playerId, int(message))

            # cancel a waiting game
            elif status['value'] == 'CANCEL_WAITING_GAME':
                if message == 'yes':
                    Telegram.sendMessage(playerId, 'you canceled the game')
                    chatStatus.remove({'pid' : playerId})
                    # !!!
            else:
                print("other type message")
def listen():
    offset = 0
    while True:
        sleep(1)
        url = 'https://api.telegram.org/bot355337431:AAEUnP4LyZoNHfJckw0Opb6-9R5brdlvnIU/getUpdates?offset=' + str(offset)
        response = requests.get(url)
        content = response.content.decode("utf-8")
        jsonResult = json.loads(content)
        messageList = jsonResult['result']
        for message in messageList:
            
            updateId = message['update_id']
            playerId = message['message']['from']['id']
            text     = message['message']['text']
            messageRecieved(playerId, text)

            if updateId >= offset:
                offset = updateId+1
# run code
listen()