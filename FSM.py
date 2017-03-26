from pymongo import MongoClient
from time import *
import requests
import json
import fileinput
import numbers
import random
#   =========================================================================================
#                                       CONFIGURATIONS
#   =========================================================================================
import Telegram;

collections = {}
debug = False
roundCount = 3

def init(clc):
    Telegram.init(clc)
    global collections
    collections = clc

#   =========================================================================================
#                                       BASE FUNCTIONS
#   =========================================================================================
def setState(member, state):
    collections['members'].update({"_id": member['_id']}, {"$set" : {"state" : state}})

def getState(member):
    for s in collections['members'].find({'_id': member['_id']}):
        return s['state']
    return 'null'

#   =========================================================================================
#                                      STATUS FUNCTIONS
#   =========================================================================================

#   ====================================  STATE  NULL  ======================================
def stateNull(member, message):
    if message == '/start':
        if member['name'] == 'null':
            member['state'] = 'reg0'
            collections['members'].insert(member)

            Telegram.wellcomeMessage(member)
#   ====================================  STATE  M0  ========================================
def reg0(member, message):
    collections['members'].update({"_id": member['_id']}, {"$set": {
        'name': message,
        'state': 'ready',
        'cart' : []
        }})

    member['name'] = message
    Telegram.registered(member)
#   ====================================  STATE  M1  ========================================
def stateM1(player, message, currentState):
    if   message == '/start':
        Telegram.wellcomeMessageToRegistered(player)
    elif message == '/help':
        Telegram.helpMessage(player)
    elif message == '/create':
        # next state
        currentState['value'] = 'G0'
        setState(currentState)
        # actions
        Telegram.createGame(player)
    elif message.startswith("/join"):
        parts = message.split("_")
        if len(parts) == 1:
            # next state
            currentState['value'] = 'G3'
            setState(currentState)
            # actions
            Telegram.gameAskId(player)
        elif len(parts) == 2:
            print(parts)
            game = 'null'
            for g in collections['games'].find({'_id': parts[1]}):
                game = g

            if game == 'null':
                Telegram.gameIdNotFound(player)
            elif game['status'] != 'WAITING':
                Telegram.cantJoinGameStartedOrFinished(player)
            elif int(game['bet']) > int(player['score']):
                Telegram.cantJoinNotEnoughBet(player, game)
            else:
                # next state
                currentState['value'] = 'G1'
                currentState['gameId'] = game['_id']
                setState(currentState)
                # action
                Telegram.gameInfo(player, game)
#   ====================================  STATE  G0  ========================================
def stateG0(player, message, currentState):
    if message.isdigit():
        bet = int(message)
        if player['score'] < bet:
            Telegram.notEnoughBetForCreate(player)
        else:
            # next state
            currentState['value'] = 'G2'
            currentState['gameId'] = "game{0}".format(collections['games'].count({}))
            setState(currentState)

            # actions
            game = {
              "_id": "game{0}".format(collections['games'].count({})),
              "creator": player,
              "plays": [],
              "word": "null",
              "bet": bet,
              "status": "WAITING",
              "scores": [0, 0],
              "winner" : "null",
              "gameState" : "W0",
              "players": [player]
            }
            gameId = collections['games'].insert_one(game).inserted_id
            game['_id'] = gameId

            Telegram.gameCreated(player, game)
    elif message == '/cancel':
        # next state
        currentState['value'] = 'M1'
        setState(currentState)
#   ====================================  STATE  G1  ========================================
def stateG1(player, message, currentState):
    if   message == 'yes':
        # next state
        currentState['value'] = 'G4'
        setState(currentState)

        # actions
        game = 'null'
        for g in collections['games'].find({'_id': currentState['gameId']}):
            game = g

        game['players'].append(player)
        collections['games'].update({'_id': game['_id']},{'$set':{'players': game['players']}})

        Telegram.playerJoined(player, game)
        for p in game['players']:
            if p['_id'] != player['_id']:
                Telegram.playerJoinedForOthers(p, game)

        if len(game['players']) == 4:
            eventGameStarted(game)

    elif message == 'no':
        # next state
        currentState['value'] = 'M1'
        setState(currentState)

    elif message == '/cancel':
        # next state
        currentState['value'] = 'M1'
        setState(currentState)
#   ====================================  STATE  G2  ========================================
def stateG2(player, message, currentState):
    if message == "/cancel":
        game = 'null'
        for g in collections['games'].find({'_id': currentState['gameId']}):
            game = g
        # next state
        for p in game['players']:
            setState({'pid': player['_id'], 'value': 'M1'})
        # actions
        Telegram.gameCanceled(player, message)
        for p in game['players']:
            if p['_id'] != player['_id']:
                setState({'pid': p['_id'], 'value': 'M1'})
                Telegram.gameCanceledForOthers(p, game)

        collections['games'].update({'_id': game['_id']},{'$set':{'status': 'CANCELED'}})

#   ====================================  STATE  G3  ========================================
def stateG3(player, message, currentState):
    gameId = message
    for g in collections['games'].find({'_id': gameId}):
        game = g

    if game == 'null':
        Telegram.gameIdNotFound(player)
    elif game['status'] != 'WAITING':
        Telegram.cantJoinGameStartedOrFinished(player)
    elif int(game['bet']) > int(player['score']):
        Telegram.cantJoinNotEnoughBet(player, game)
    else:
        # next state
        currentState['value'] = 'G1'
        currentState['gameId'] = game['_id']
        setState(currentState)
        # action
        Telegram.gameInfo(player, game)
#   ====================================  STATE  G4  ========================================
def stateG4(player, message, currentState):
    if message == "/cancel":
        game = 'null'
        for g in collections['games'].find({'_id': currentState['gameId']}):
            game = g
        # next state
        for p in game['players']:
            setState({'pid': player['_id'], 'value': 'M1'})
        # actions
        Telegram.playerLeftGame(player)
        for p in game['players']:
            if p['_id'] != player['_id']:
                Telegram.playerLeftGameForOther(p, game)

        for i in range(0, len(game['players'])-1):
            if player['_id'] == game['players'][i]['_id']:
                del game['players'][i]
        collections['games'].update({'_id': game['_id']},{'$set':{'players': game['players']}})
#   ====================================  STATE  P0  ========================================
def stateP1(player, message, currentState):
    pass
#   ====================================  STATE  P1  ========================================
def stateP2(player, message, currentState):
    game = collections['games'].find_one({'_id': currentState['gameId']})
    
    
    gameState = game['gameState']
    turnIndex = len(game['plays']) -1
    
    #    INPUT VALIDATION START
    
    #           !!!!!!

    #    INPUT VALIDATION  END
    
    if   gameState == 'W1':
        game['word'] = message

        lastPlay = game['plays'][-1]
        lastPlay['steps'].append({
            "player" : player,
            "value"  : message
            })

        collections['games'].update({'_id': game['_id']},{'$set':{
            'gameState' : 'W2',
            'word' : message,
            "plays" : game['plays']
            }})
        for p in game['players']:
            if p['job'] == turnJob(turnIndex, 2):
                setState({
                    'pid': p['_id'],
                    'value' : 'P2',
                    'gameId' : game['_id'],
                    })
                Telegram.startedWord(p, game)
            else:
                setState({
                    'pid': p['_id'],
                    'value' : 'P1',
                    'gameId' : game['_id'],
                    })
    elif gameState == 'W2':

        lastPlay = game['plays'][-1]
        lastPlay['steps'].append({
            "player" : player,
            "value"  : message
        })
        collections['games'].update({'_id': game['_id']},{'$set':{
            'gameState' : 'W3',
            "plays" : game['plays']
        }})
        for p in game['players']:
            if p['job'] == turnJob(turnIndex, 3):
                setState({
                    'pid': p['_id'],
                    'value' : 'P2',
                    'gameId' : game['_id'],
                    })
                Telegram.helpedToTeamMate(p, game)
            else:
                setState({
                    'pid': p['_id'],
                    'value' : 'P1',
                    'gameId' : game['_id'],
                    })
                if p['job'] in [turnJob(turnIndex, 0), turnJob(turnIndex, 1)]:
                    Telegram.helpedToOpponents(p, game)
    elif gameState == 'W3':

        lastPlay = game['plays'][-1]
        lastPlay['steps'].append({
            "player" : player,
            "value"  : message
        })
        
        collections['games'].update({'_id': game['_id']},{'$set':{
            'gameState' : 'W4',
            "plays" : game['plays']
        }})
        if game['word'] == message:

            currentPlayer = player
            for p in game['players']:
                if p['_id'] == currentPlayer['_id']:
                    currentPlayer = p

            winnerTeam = currentPlayer['job']%2

            lastPlay['status'] = winnerTeam
            game['scores'][winnerTeam] += 1
            collections['games'].update({'_id': game['_id']},{'$set':{
                'scores' : game['scores']
            }})

            if game['scores'][winnerTeam] == roundCount:
                game['winner'] = winnerTeam
                game['status'] = 'FINISHED'
                for p in game['players']:
                    if p['job'] in [turnJob(turnIndex, winnerTeam*2), turnJob(turnIndex, winnerTeam*2 +1)]:
                        Telegram.lostPlay(p, game, roundCount)
                    else:
                        Telegram.wonPlay(p, game, roundCount)
            else:
                game['winner'] = winnerTeam
                game['status'] = 'FINISHED'

                for p in game['players']:
                    if p['job'] in [turnJob(turnIndex, winnerTeam*2), turnJob(turnIndex, winnerTeam*2 +1)]:
                        Telegram.lostPlay(p, game, roundCount)
                    else:
                        Telegram.wonPlay(p, game, roundCount)

                startPlay(game)
        else:
            for p in game['players']:
                if p['job'] == turnJob(turnIndex, 0):
                    setState({
                        'pid': p['_id'],
                        'value' : 'P2',
                        'gameId' : game['_id'],
                        })
                    Telegram.guessedToOpponents(p, game)
                    Telegram.helpOrder(p)
                else:
                    setState({
                        'pid': p['_id'],
                        'value' : 'P1',
                        'gameId' : game['_id'],
                        })
                    if p['job'] == turnJob(turnIndex, 1):
                        Telegram.guessedToOpponents(p, game)
                    elif p['job'] == turnJob(turnIndex, 2):
                        Telegram.guessedToTeamMate(p, game)

    elif gameState == 'W4':
        lastPlay = game['plays'][-1]
        lastPlay['steps'].append({
            "player" : player,
            "value"  : message
        })
        collections['games'].update({'_id': game['_id']},{'$set':{
            'gameState' : 'W5',
            "plays" : game['plays']
        }})
        for p in game['players']:
            if p['job'] == turnJob(turnIndex, 1):
                setState({
                    'pid': p['_id'],
                    'value' : 'P2',
                    'gameId' : game['_id'],
                    })
                Telegram.helpedToTeamMate(p, game)
            else:
                setState({
                    'pid': p['_id'],
                    'value' : 'P1',
                    'gameId' : game['_id'],
                    })
                if p['job'] in [turnJob(turnIndex, 2), turnJob(turnIndex, 3)]:
                    Telegram.helpedToOpponents(p, game)


    elif gameState == 'W5':

        lastPlay = game['plays'][-1]
        lastPlay['steps'].append({
            "player" : player,
            "value"  : message
        })
        collections['games'].update({'_id': game['_id']},{'$set':{
            'gameState' : 'W2',
            "plays" : game['plays']
        }})
        if game['word'] == message:
            currentPlayer = player
            for p in game['players']:
                if p['_id'] == currentPlayer['_id']:
                    currentPlayer = p

            winnerTeam = currentPlayer['job']%2

            lastPlay['status'] = winnerTeam
            game['scores'][winnerTeam] += 1
            collections['games'].update({'_id': game['_id']},{'$set':{
                'scores' : game['scores']
            }})
            

            if game['scores'][winnerTeam] == roundCount:
                game['winner'] = winnerTeam
                game['status'] = 'FINISHED'

                for p in game['players']:
                    if int(p['job']/2) == winnerTeam:
                        collections['players'].update({'_id': p['_id']},{'$set':{'score': p['score'] + game['score']}})
                        p['score'] += game['score']
                        Telegram.wonGame(p, game)
                    else:
                        collections['players'].update({'_id': p['_id']},{'$set':{'score': p['score'] - game['score']}})
                        p['score'] -= game['score']
                        Telegram.lostGame(p, game)

            else:
                for p in game['players']:
                    if p['job'] in [turnJob(turnIndex, 2), turnJob(turnIndex, 3)]:
                        Telegram.lostPlay(p, game, roundCount)
                    elif p['job'] in [turnJob(turnIndex, 0), turnJob(turnIndex, 1)]:
                        Telegram.wonPlay(p, game, roundCount)
                startPlay(game)

        else:
            for p in game['players']:
                if p['job'] == turnJob(turnIndex, 2):
                    setState({
                        'pid': p['_id'],
                        'value' : 'P2',
                        'gameId' : game['_id'],
                        })
                    Telegram.guessedToOpponents(p, game)
                    Telegram.helpOrder(p)
                else:
                    setState({
                        'pid': p['_id'],
                        'value' : 'P1',
                        'gameId' : game['_id'],
                        })
                    if p['job'] == turnJob(turnIndex, 3):
                        Telegram.guessedToOpponents(p, game)
                    elif p['job'] == turnJob(turnIndex, 0):
                        Telegram.guessedToTeamMate(p, game)