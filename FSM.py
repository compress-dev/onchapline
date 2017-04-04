from pymongo import MongoClient
from time import *
from bson.objectid import ObjectId
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
import shop
collections = {}
debug = False
roundCount = 3
commandTemplate = {}

def init(clc):
    Telegram.init(clc)
    shop.init(clc)

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
    if not isinstance(message, str):
        return False

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
        orders = []
        for cart in collections['orders'].find({'orders.status':{'$not': {'$eq': 'DELIVERED'}}}):
            for i in range(0, len(cart['orders'])):
                if cart['orders'][i]['status'] != 'DELIVERED':
                    Telegram.orderInfoMessage(member, cart, i)
        return True

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
    
    elif message == '/accept_cart':
        setState(member, 'cart-address', {})
        Telegram.cartAddress(member)
        return True

    elif message == 'مشاهده سبد خرید':
        cart = member['cart']
        for i in range(0, len(cart)):
            Telegram.cartOrder(member, cart[i], i)

        Telegram.cartAccept(member, member['cart'])
        return True

    elif message.startswith("/remove_"):
        orderIndex = int(message.split("_")[1])
        del member['cart'][orderIndex]
        collections['members'].update({'_id': member['_id']},{ "$set": {'cart': member['cart']}})
        Telegram.cartOrderRemoved(member)
        return True

    elif message.startswith('/accept_order_'):
        parts = message.split("_")
        cartId = parts[2]
        orderIndex = int(parts[3])

        cart = collections['orders'].find_one({'_id': ObjectId(cartId)})
        orders = cart['orders']
        orders[orderIndex]['status'] = 'ACCEPTED'
        
        collections['orders'].update({'_id': ObjectId(cartId)}, {'$set': {'orders': orders}})
        
        Telegram.orderAcceptPrint(member)
        Telegram.orderAcceptMember(cart['sender'], cart, orderIndex)

    elif message.startswith('/message_order_'):
        parts = message.split("_")
        cartId = parts[2]
        orderIndex = int(parts[3])

        cart = collections['orders'].find_one({'_id': ObjectId(cartId)})
        
        receiver = 'null'
        if member['_id'] == cart['sender']['_id']:
            receiverId = cart['orders'][orderIndex]['product']['chat_id']
            receiver = collections['members'].find_one({'_id': int(receiverId)})
        else:
            receiver = cart['sender']
        
        setState(member, 'order-message',
            {
                'cart': cart,
                'order-index': orderIndex,
                'receiver': receiver
            })
        Telegram.orderMessage(member)
    elif message.startswith('/refuse_order_'):
        parts = message.split("_")
        cartId = parts[2]
        orderIndex = int(parts[3])

        cart = collections['orders'].find_one({'_id': ObjectId(cartId)})
        orders = cart['orders']
        orders[orderIndex]['status'] = 'REFUSED'

        collections['orders'].update({'_id': ObjectId(cartId)}, {'$set': {'orders': orders}})

        Telegram.orderRefusePrint(member)
        Telegram.orderRefuseMember(cart['sender'], cart, orderIndex)
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
#   ====================================  STATE  search product title  ======================================
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
        product = ServerAPI.getProductById(message.split("_")[1])
        setState(member, 'order-count', 
            {
                'product': product,
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset']
            })
        Telegram.productCount(member,product)
    
    else:
        if isKeyword(message):
            setState(member, 'ready', {})
            state_ready(member, message)
        else:
            products = ServerAPI.searchProductsByTitle(message)

            for product in products:
                Telegram.product(member, product)

            Telegram.moreProducts(member)
            collections['members'].update({'_id': member['_id']}, {"$set" : {'state_extra' : {'search': message, 'offset': 5}}})

#   ====================================  STATE  order count  ========================================
def state_order_count(member, message):
    if mainMenu(member, message):
        return True
    if message == '/cancel':
        setState(member, 'search-product-title', 
            {
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset']
            })
    elif message.isdigit():
        cart = {
                    'product' : member['state_extra']['product'],
                    'count': int(message),
                    'files': [],
                    'description': 'null',
                    'messages': []
                }
        Telegram.orderDescription(member, cart)
        setState(member, 'order-description', 
            {
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset'],
                'cart'   : cart
            })
    else:
        setState(member, 'ready', {})
        state_ready(member, message)
#   ====================================  STATE  order description  ========================================
def state_order_description(member, message):
    if mainMenu(member, message):
        return True
    if message == '/cancel':
        setState(member, 'search-product-title', 
            {
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset']
            })
    else:
        if isKeyword(message):
            setState(member, 'ready', {})
            state_ready(member, message)
        else:
            cart = member['state_extra']['cart']
            cart['description'] = message
            setState(member, 'order-file', 
                {
                    'search' : member['state_extra']['search'],
                    'offset' : member['state_extra']['offset'],
                    'cart'   : cart
                })
            Telegram.orderFile(member, cart)
#   ====================================  STATE  order file  ========================================
def state_order_file(member, message):
    if mainMenu(member, message):
        return True
    if message == '/cancel':
        
        setState(member, 'search-product-title', 
            {
                'search' : member['state_extra']['search'],
                'offset' : member['state_extra']['offset']
            })
    elif message == '/upload_finish':
        
        setState(member, 'ready', 
            {})
        collections['members'].update({'_id': member['_id']}, {"$push" : {'cart' : member['state_extra']['cart']}})
        member['cart'].append(member['state_extra']['cart'])
        Telegram.cartAccept(member, member['cart'])
    else:
        if isKeyword(message):
            setState(member, 'ready', {})
            state_ready(member, message)
        else:
            cart = member['state_extra']['cart']
            if 'document' in message:
                cart['files'].append({'type': 'document', 'file': message})
            if 'audio' in message:
                cart['files'].append({'type': 'audio', 'file': message})
            if 'photo' in message:
                cart['files'].append({'type': 'photo', 'file': message})
            if 'video' in message:
                cart['files'].append({'type': 'video', 'file': message})
            if 'voice' in message:
                cart['files'].append({'type': 'voice', 'file': message})
            if 'contact' in message:
                cart['files'].append({'type': 'contact', 'file': message})

            setState(member, 'order-file', 
                {
                    'search' : member['state_extra']['search'],
                    'offset' : member['state_extra']['offset'],
                    'cart'   : cart
                })
            Telegram.orderFileAgain(member, cart)
#   ====================================  STATE  cart address message  ========================================
def state_cart_address_text(member, message):
    if mainMenu(member, message):
        return True
    if message == '/cancel':
        setState(member, 'ready', 
            {})
    else:
        if isKeyword(message):
            setState(member, 'ready', {})
            state_ready(member, message)
        else:
            cart = member['cart']
            #cart['address'] = 
            setState(member, 'cart-accept-ask', 
                {
                    'address' : message,
                })
            Telegram.cartAcceptAsk(member, cart)
#   ====================================  STATE  cart confirm acception  ========================================
def state_cart_accept(member, message):
    if mainMenu(member, message):
        return True
    if message == '/cancel' or message == "/no":
        setState(member, 'ready', 
            {})
    elif message == "/yes":
        shop.acceptCart(member)
        setState(member, 'ready',
            {})
        Telegram.cartAcceptDone(member)
    else:
        setState(member, 'ready', {})
        state_ready(member, message)
#   ====================================  STATE  cart confirm acception  ========================================
def state_message(member, message, isFile = False):
    if mainMenu(member, message):
        return True
    if message == '/cancel':
        setState(member, 'ready', 
            {})
    else:
        orderIndex = member['state_extra']['order-index']

        collections['orders'].update({'_id': ObjectId(member['state_extra']['cart']['_id'])}, {'$push' : 
            {'orders.{0}.messages'.format(orderIndex): 
                {
                    'message': message,
                    'sender' : member,
                    'type'   : 'text'
                }
            }})
        if isFile:
            pass
        else:  
            if isKeyword(message):
                setState(member, 'ready', {})
                state_ready(member, message)
            else:
                Telegram.orderTextMessage(member['state_extra']['receiver'], message, member['state_extra']['cart'], orderIndex)

# ========================================= RESERVED KEYWORDS ===============================================
def isKeyword(message):
    if message == 'بیشتر':
        return 1
    elif message == 'جستجوی محصولات':
        return 2
    elif message == 'جستجوی پیشرفته محصولات':
        return 3
    elif message == 'لیست سفارشات در حال اجرا':
        return 4
    elif message == 'مشاهده سبد خرید':
        return 5
    elif message == 'بسه!':
        return 6
    elif message == 'بیشتر بیار':
        return 7
    elif message == '/cancel':
        return 8
    elif message == '/accept_cart':
        return 9
    elif message == '/start':
        return 10
    elif message == '/more':
        return 11
    elif message.startswith('/remove_'):
        return 12
    elif message.startswith('/take_'):
        return 13
    elif message.startswith('/accept_order_'):
        return 14
    elif message.startswith('/message_order_'):
        return 15
    elif message.startswith('/refuse_order_'):
        return 16
    elif message == '/upload_finish':
        return 17
    elif message == '/yes':
        return 18
    elif message == '/no':
        return 19
    else:
        return 0