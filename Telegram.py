from pymongo import MongoClient
import time
import requests
import json

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
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendMessage?chat_id=' + str(memberId) + '&text=' + message
        
        #{"keyboard":[[{"text": "yes 1"},{"text":"no"}]]}
        keyboard = json.dumps(keyboard)
        url += '&reply_markup=' + keyboard

        allowedMessages = json.dumps(["message", "inline_query", "chosen_inline_result", "callback_query"])
        url += '&allowed_updates=' + allowedMessages

        response = requests.get(url)
        content = response.content.decode("utf-8")
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
def wellcomeMessage(member):
    message = messagesTemplate["welcome"]['text']
    sendMessage(member, message)

def registered(member):
    message =  messagesTemplate["registered"]['text'].format(member['name'])
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

