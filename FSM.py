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
commandTemplate = {}

def init(clc):
    Telegram.init(clc)
    global collections
    collections = clc

    global commandTemplate
    commandTemplate = json.loads(open("command-template.json", 'r', encoding="utf-8").read())


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
#   ====================================  STATE  reg0  ========================================
def state_reg0(member, message):
    collections['members'].update({"_id": member['_id']}, {"$set": {
        'name': message,
        'state': 'ready',
        'cart' : []
        }})

    member['name'] = message
    Telegram.registered(member)

#   ====================================  STATE  ready  ========================================
def state_ready(member, message):
    if message == commandTemplate['help']['text']:
        pass
    elif message == commandTemplate['search-product-title']['text']:
        pass
    elif message == commandTemplate['search-print-title']['text']:
        pass
    elif message == commandTemplate['search-full']['text']:
        pass
    elif message == commandTemplate['all-orders']['text']:
        pass
    elif message == commandTemplate['active-orders']['text']:
        pass