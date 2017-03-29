from pymongo import MongoClient
import time
import requests
import json
import urllib
#   =========================================================================================
#                                       CONFIGURATIONS
#   =========================================================================================
collections = {}
messagesTemplate = {}
keyboardTemplate = {}
debug = False

def init(clc):
    global collections
    collections = clc

    global messagesTemplate
    messagesTemplate = json.loads(open("messages-template.json", 'r', encoding="utf-8").read())
    global keyboardTemplate
    keyboardTemplate = json.loads(open("keyboard-template.json", 'r', encoding="utf-8").read())

#   =========================================================================================
#                                    BASE-LAYERED FUNCTION
#   =========================================================================================
def sendMessage(member , message = 'test(keyboard removed)', keyboard = {"remove_keyboard": True}):
    memberId = member['_id']
    if debug:
        if 'remove_keyboard' not in keyboard:
            message += " (";
            for key in keyboard:
                message += key['text'] + ','
            message += ")"

        print("{0}:\n{1}\n-----------------------------".format(member['name'], message))
        return True
    else:
        inputs = {
            'chat_id' : str(memberId),
            'parse_mode': 'HTML',
            'text' : message
        }
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendMessage?'
        
        #{"keyboard":[[{"text": "yes 1"},{"text":"no"}]]}
        keyboard = json.dumps(keyboard)
        inputs['reply_markup'] = keyboard

        allowedMessages = json.dumps(["message", "inline_query", "chosen_inline_result", "callback_query"])
        inputs['allowed_updates'] = allowedMessages

        url += urllib.parse.urlencode(inputs)
        response = requests.get(url)
        content = response.content.decode("utf-8")
        print(content)
        jsonResult = json.loads(content)
        return jsonResult['ok']

def getMessageString(messageId):
    for message in collections['messages'].find({'_id': messageId}):
        return message['text']
    return False

def getKeyboard(keyboardId):
    for keyboard in collections['keyboards'].find({'_id': keyboardId}):
        return keyboard['keyboard']
    return False
#   =========================================================================================
#                                 LAST CHAIN LAYER FUNCTIONS
#   =========================================================================================

#       REGISTRATION
def nameRequire(member):
    message = messagesTemplate["name-require"]['text']
    sendMessage(member, message)

def phoneRequire(member):
    message =  messagesTemplate["phone-require"]['text'].format(member['name'])
    sendMessage(member, message)

def registered(member):
    message =  messagesTemplate["registered"]['text'].format(member['name'], member['phone'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def help(member):
    message =  messagesTemplate["help"]['text']
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchByOffice(member):
    message =  messagesTemplate["search-office"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchByProduct(member):
    message =  messagesTemplate["search-product"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchAdvancedScoreMin(member):
    message =  messagesTemplate["search-advanced-score-min"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchAdvancedPriceMin(member):
    message =  messagesTemplate["search-advanced-price-min"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchAdvancedScoreMax(member):
    message =  messagesTemplate["search-advanced-score-max"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchAdvancedPriceMax(member):
    message =  messagesTemplate["search-advanced-price-max"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchAdvancedPriceAccept(member):
    message =  messagesTemplate["search-advanced-price-max"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def searchAdvancedScoreAccept(member):
    message =  messagesTemplate["search-advanced-score-accept"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def product(member, product):
    message =  messagesTemplate["product-message"]['text'].format(
        product['image']
        , product['title']
        , product['office']
        , product['amount']
        , product['price']
        , product['deposit']
        , product['score']
        , product['id'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def moreProducts(member):
    message =  messagesTemplate["more-products"]['text']
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def productCount(member):
    message =  messagesTemplate["product-count"]['text']
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def orderDescription(member, cart):
    print(cart)
    message =  messagesTemplate["order-description"]['text'].format(
        int(cart['count']) * int(cart['product']['amount']),
        cart['product']['title'],
        cart['product']['office'])

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def orderFile(member, cart):
    message =  messagesTemplate["order-file"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def orderFileAgain(member, cart):
    message =  messagesTemplate["order-file-again"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def cartAccept(member, cart):
    message =  messagesTemplate["cart-acceptable"]['text'].format(len(cart))

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def cartAddress(member):
    message =  messagesTemplate["cart-address"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def cartAcceptAsk(member, cart):
    message =  messagesTemplate["cart-info-accept"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def cartAcceptDone(member):
    message =  messagesTemplate["cart-acception-done"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)
    