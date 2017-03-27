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
import Telegram
import ServerAPI

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
def setState(member, state, state_extra = {}):
    collections['members'].update({"_id": member['_id']}, {"$set" : {"state" : state, 'state_extra': state_extra}})

def getState(member):
    for s in collections['members'].find({'_id': member['_id']}):
        return s['state']
    return 'null'

def mainMenu(member, message):
    if message == "بیشتر":
        Telegram.help(member)
        return True
    elif message == "جستجوی محصولات":
        Telegram.searchByProduct(member)
        setState(member, 'search-product-title')
        return True
    elif message == "جستجوی پیشرفته محصولات":
        return True
        pass
    elif message == "لیست سفارشات در حال اجرا":
        return True
        pass

    # more commands
    elif message == "informations":
        Telegram.help(member)
        return True
    elif message == "جستجوی چاپخانه ها":
        Telegram.searchByOffice(member)
        setState(member, 'search-office-title')
        return True
    elif message == "لیست سفارشات ارسال شده":
        return True
        pass
#   =========================================================================================
#                                      STATUS FUNCTIONS
#   =========================================================================================

#   ====================================  STATE  NULL  ======================================
def stateNull(member, message):
    if message == '/start':
        if member['name'] == 'null':
            member['state'] = 'reg0'
            collections['members'].insert(member)

            Telegram.nameRequire(member)

#   ====================================  STATE  reg0  ========================================
def state_reg0(member, message):
    collections['members'].update({"_id": member['_id']}, {"$set": {
        'name': message,
        'state': 'reg1'
        }})

    member['name'] = message
    Telegram.phoneRequire(member)

#   ====================================  STATE  reg1  ======================================
def state_reg1(member, message):
    collections['members'].update({"_id": member['_id']}, {"$set": {
        'phone': message,
        'state': 'ready',
        'cart' : []
        }})

    member['phone'] = message
    Telegram.registered(member)
#   ====================================  STATE  ready  ========================================
def state_ready(member, message):
    return mainMenu(member, message)
#   ====================================  STATE  reg1  ======================================
def state_search_product_title(member, message):
    if mainMenu(member, message):
        return True
    
    if message == '/more':
        
        products = ServerAPI.searchProductsByTitle(member['state_extra']['search'])
        collections['members'].update({'_id': member['_id']}, {"$set" : {'state_extra' : {'search': member['state_extra']['search'] ,'offset': 5 + member['state_extra']['offset']}}})
        for product in products:
            Telegram.product(member, product)
        Telegram.moreProducts(member)
    
    elif message.startswith('/take'):

        setState(member, 'take-product', 
            {
                'productId': message.split("_")[1], 
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset']
            })
        Telegram.productCount(member)

    else:
        
        products = ServerAPI.searchProductsByTitle(message)
        for product in products:
            Telegram.product(member, product)
        Telegram.moreProducts(member)
        collections['members'].update({'_id': member['_id']}, {"$set" : {'state_extra' : {'search': message, 'offset': 5}}})
#   ====================================  STATE  ready  ========================================
def state_take_product(member, message):
    if mainMenu(member, message):
        return True
    if message == '/cancel':
        setState(member, 'search-product-title', 
            {
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset']
            })
    elif isdigit(message):
        product = getProductById(member['state_extra']['id'])
        setState(member, 'search-product-title', 
            {
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset'],
                'cart' : {
                    'product' : product,
                    'count': count,
                    'files': []
                }
            })
