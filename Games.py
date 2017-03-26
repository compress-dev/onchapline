from pymongo import MongoClient
from time import *
import requests
import json

import Telegram


playersCollection = 'null'
gamesCollection = 'null'
chatStatus = 'null'

def createGame(playerId, bet):
    print('game created by ' + str(playerId) + ' in bet ' + str(bet))
    player = 'NULL'
    for p in playersCollection.find({'_id' : playerId}):
        player = p
        break

    if player == 'NULL':
        return False
    gamesCollection.insert({
        'status' : 'WAITING',
        'job' : 'NULL',
        'creator' : player,
        'players' : [
                player
            ],
        'word' : 'NULL',
        'bet' : bet
        })
    chatStatus.remove({'pid' : playerId})
    Telegram.sendMessage(playerId, 'your game created game Id is ' + str(1))