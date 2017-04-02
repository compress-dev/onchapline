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
    keyboard = {'inline_keyboard':[[{"text":"انتخاب","callback_data":"/take_{0}".format(product['id'])}]]}

    sendMessage(member, message, keyboard)

def moreProducts(member):
    message =  messagesTemplate["more-products"]['text']
    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def productCount(member, product):
    message =  messagesTemplate["product-count"]['text'].format(product['amount'], int(product['amount'])*2)
    
    keyboard = {'inline_keyboard':[
        [
        {"text":"از این سفارش منصرف شدم","callback_data":"/cancel"}]
        ]}

    sendMessage(member, message, keyboard)

def orderDescription(member, cart):
    message =  messagesTemplate["order-description"]['text'].format(
        int(cart['count']) * int(cart['product']['amount']),
        cart['product']['title'],
        cart['product']['office'])

    keyboard = {'inline_keyboard':[
        [
        {"text":"توضیحی ندارم","callback_data":"none"},
        {"text":"از سفارش منصرف شدم","callback_data":"/cancel"}
        ]
        ]}
    sendMessage(member, message, keyboard)

def orderFile(member, cart):
    message =  messagesTemplate["order-file"]['text']

    keyboard = {'inline_keyboard':[
        [
        {"text":"فایل برای آپلود ندارم","callback_data":"/upload_finish"},
        {"text":"از سفارش منصرف شدم","callback_data":"/cancel"}
        ]
        ]}
    sendMessage(member, message, keyboard)

def orderFileAgain(member, cart):
    message =  messagesTemplate["order-file-again"]['text']

    keyboard = {'inline_keyboard':[
        [
        {"text":"تمام شدند","callback_data":"/upload_finish"},
        {"text":"از سفارش منصرف شدم","callback_data":"/cancel"}
        ]
        ]}
    sendMessage(member, message, keyboard)

def cartAccept(member, cart):
    message =  messagesTemplate["cart-acceptable"]['text'].format(len(cart))

    keyboard = {'inline_keyboard':[
        [
        {"text":"ارسال سبد خرید به چاپخانه ها","callback_data":"/accept_cart"},
        {"text":"مشاهده سبد خرید","callback_data":"مشاهده سبد خرید"}
        ]
        ]}
    sendMessage(member, message, keyboard)

def cartAddress(member):
    message =  messagesTemplate["cart-address"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def cartAcceptAsk(member, cart):
    message =  messagesTemplate["cart-info-accept"]['text']

    keyboard = {'inline_keyboard':[
        [
        {"text":"بلی","callback_data":"/yes"},
        {"text":"خیر","callback_data":"/no"}
        ]
        ]}
    sendMessage(member, message, keyboard)

def cartAcceptDone(member):
    message =  messagesTemplate["cart-acception-done"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def cartOrder(member, order, orderIndex):
    message =  messagesTemplate["cart-order"]['text'].format(
        order['product']['title'], 
        order['product']['office'], 
        int(order['product']['amount'])*int(order['count']),
        int(order['product']['price'])*int(order['count']),
        order['product']['deposit'])

    keyboard = {'inline_keyboard':[[{"text":"حذف","callback_data":"/remove_{0}".format(orderIndex)}]]}
    sendMessage(member, message, keyboard)

def cartOrderRemoved(member):
    message =  messagesTemplate["order-remove"]['text'].format(len(member['cart']))

    keyboard = {'inline_keyboard':[[{"text":"ارسال سبد خرید به چاپخانه ها","callback_data":"/accept_cart"}]]}
    sendMessage(member, message, keyboard)

def orderForPrint(cart, orderIndex):
    message =  messagesTemplate["cart-order-print"]['text'].format(
        cart['orders'][orderIndex]['product']['title'],
        int(cart['orders'][orderIndex]['product']['amount'])*int(cart['orders'][orderIndex]['count']),
        int(cart['orders'][orderIndex]['product']['price'])* int(cart['orders'][orderIndex]['count']),
        cart['orders'][orderIndex]['sender']['name'], 
        cart['address'],
        cart['orders'][orderIndex]['description'])

    keyboard = {'inline_keyboard':[[
        {"text":"تایید سفارش","callback_data":"/accept_order_{0}_{1}".format(cart['_id'], orderIndex)},
        {"text":"ارسال پیام","callback_data":"/message_order_{0}_{1}".format(cart['_id'], orderIndex)},
        {"text":"رد سفارش","callback_data":"/refuse_order_{0}_{1}".format(cart['_id'], orderIndex)}
        ]]}

    member = { '_id': cart['orders'][orderIndex]['product']['chat_id']}
    sendMessage(member, message, keyboard)
    for f in cart['orders'][orderIndex]['files']:
        sendFile(member, f['file'], f['type'])

def sendFile(member, file, fileType):
    caption = ''
    if 'caption' in file:
        caption = file['caption']

    if fileType == 'document':
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendDocument?'
        inputs = {
            'chat_id' : str(member['_id']),
            'document': file['document']['file_id'],
            'caption' : caption
        }
    if fileType == 'audio':
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendAudio?'
        inputs = {
            'chat_id' : str(member['_id']),
            'audio': file['audio']['file_id'],
            'title': file['audio']['title'],
            'caption' : caption
        }
    if fileType == 'photo':
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendPhoto?'
        inputs = {
            'chat_id' : str(member['_id']),
            'photo': file['photo'][-1]['file_id'],
            'caption' : caption
        }
    if fileType == 'video':
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendVideo?'
        inputs = {
            'chat_id' : str(member['_id']),
            'video': file['video']['file_id'],
            'caption' : caption
        }
    if fileType == 'voice':
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendVoice?'
        inputs = {
            'chat_id' : str(member['_id']),
            'voice': file['voice']['file_id'],
            'caption' : caption
        }

    url += urllib.parse.urlencode(inputs)
    response = requests.get(url)

def orderAcceptPrint(member):
    message =  messagesTemplate["order-accept-print"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def orderRefusePrint(member):
    message =  messagesTemplate["order-refuse-print"]['text']

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)

def orderAcceptMember(member, cart, orderIndex):
    message =  messagesTemplate["order-accept-member"]['text'].format(
        cart['orders'][orderIndex]['product']['title'], 
        int(cart['orders'][orderIndex]['product']['amount']) * int(cart['orders'][orderIndex]['count']),
        cart['orders'][orderIndex]['product']['office'])

    dep = cart['orders'][orderIndex]['product']['deposit'] * cart['orders'][orderIndex]['count']
    keyboard = {'inline_keyboard':[
    [{"text":"پرداخت {0} تومان بیعانه".format(dep),"callback_data":"/pay_order_dep_{0}_{1}".format(cart['_id'], orderIndex)}],
    [{"text":"از این سفارش انصراف می دهم".format(dep),"callback_data":"/cancel_order_{0}_{1}".format(cart['_id'], orderIndex)}]
    ]}
    sendMessage(member, message, keyboard)

def orderRefuseMember(member, cart, orderIndex):
    message =  messagesTemplate["order-refuse-member"]['text'].format(
        cart['orders'][orderIndex]['product']['title'], 
        int(cart['orders'][orderIndex]['product']['amount']) * int(cart['orders'][orderIndex]['count']),
        cart['orders'][orderIndex]['product']['office'])

    keyboard = keyboardTemplate['normal']
    sendMessage(member, message, keyboard)   

def orderTextMessage(member, message, cart, orderIndex):
    message =  messagesTemplate["order-message-text"]['text'].format(
        cart['orders'][orderIndex]['product']['title'],
        cart['orders'][orderIndex]['product']['office'],
        message)

    keyboard = {'inline_keyboard':[
    [{"text":"پاسخ دادن".format(dep),"callback_data":"/order_message_{0}_{1}".format(cart['_id'], orderIndex)}]
    ]}
    sendMessage(member, message, keyboard)
