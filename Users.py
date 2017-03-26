from pymongo import MongoClient
from time import *
import requests
import json

playersCollection = 'null'
gamesCollection = 'null'
chatStatus = 'null'

''' =========================================================================================
                last-layer functions about a single game
    =========================================================================================
'''
def register(playerId, name):
    defaultScore = 1000

    if checkPlayerName(name):
        sendMessage(playerId, 'sorry! please use another name, this name is for other player')
        return False

    playersCollection.insert({
            '_id' : playerId,
            'name': name,
            'score': defaultScore
        })
    sendMessage(playerId, 'wellcome ' + name + '\nyou have ' + str(defaultScore) + ' to start\n press /create to start a new game')
    return True

''' =========================================================================================
                get informations from a single player
    =========================================================================================
'''
def checkPlayerId(playerId):
    for player in playersCollection.find({'_id': playerId}):
        return True
    return False

def checkPlayerName(name):
    for player in playersCollection.find({'name': name}):
        return True
    return False    

def getScore(playerId):
    for player in playersCollection.find({'_id' : playerId}):
            return player['score']
    return False

def getPlayerById(playerId):
    for player in playersCollection.find({'_id' : playerId}):
            return player
    return False

def getPlayerByName(playerName):
    for player in playersCollection.find({'name' : playerName}):
            return player
    return False

def getPlayerGames(player):
    gameArray = []
    for game in gamesCollection.find({'players._id' : player['_id'], 'status': {'$in' : ['WAITING', 'PLAYING']}}):
            gameArray.append(game)

    return gameArray

''' =========================================================================================
                check player busy status about game and other operations
    =========================================================================================
'''

def isPlayerInMeeting(player):
    statusArray = []
    for status in chatStatus.find({'pid' : player['_id']}):
            statusArray.append(status)

    if len(statusArray) > 0:
        return statusArray

    return False

def isPlayerInGame(player):
    gameArray = []
    for game in gamesCollection.find({'players._id' : player['_id'], 'status': {'$in' : ['WAITING', 'PLAYING']}}):
            gameArray.append(game)

    if len(gameArray)   > 0:
        return gameArray
    return False

def isPlayerBusy(player):
    return not isPlayerInGame(player) and not isPlayerInMeeting(player)

#   =========================================================================================
#                   DEBUG AND TESTING CODE SECTION
#   =========================================================================================
if __name__ == '__main__':
    # connection to database
    print("connecting to mongodb")
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    print("connected  to mongodb")

    database = client.LongMan
    playersCollection = database.players
    gamesCollection = database.games
    chatStatus = database.chatStatus

    # main test
    player = getPlayerByName('mr-exception')
    
    print("\n... check if player mr-exception is in any game")
    print(isPlayerInGame(player))

    print("\n... check if player mr-exception is in any meeting")
    print(isPlayerInMeeting(player))

    print("\n... check if player mr-exception is busy")
    print(isPlayerBusy(player))