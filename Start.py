from pymongo import MongoClient
from time import *
import requests
import json
import fileinput
import urllib
#   =========================================================================================
#                                       CONFIGURATIONS
#   =========================================================================================
import FSM;
from values import *;


print("connecting to mongodb")
client = MongoClient('mongodb://127.0.0.1')
print("connected  to mongodb")

database = client.onchapline
collections = {
    "members"   : database.members,
    "orders"     : database.orders
}
debug = False

FSM.init(collections)

def FSMInput(member, message):
    if isinstance(message, str):
        if member['state'] == 'null':
            FSM.stateNull(member, message)
        elif member['state'] == 'reg0':
            FSM.state_reg0(member, message)
        elif member['state'] == 'reg1':
            FSM.state_reg1(member, message)
        elif member['state'] == 'ready':
            FSM.state_ready(member, message)
        elif member['state'] == 'search-product-title':
            FSM.state_search_product_title(member, message)
        elif member['state'] == 'order-count':
            FSM.state_order_count(member, message)
        elif member['state'] == 'order-description':
            FSM.state_order_description(member, message)
        elif member['state'] == 'order-file':
            FSM.state_order_file(member, message)
        elif member['state'] == 'cart-address':
            FSM.state_cart_address_text(member, message)
        elif member['state'] == 'cart-accept-ask':
            FSM.state_cart_accept(member, message)
        elif member['state'] == 'order-message':
            FSM.state_message(member, message)
    else:
        if member['state'] == 'order-file':
            FSM.state_order_file(member, message)
        elif member['state'] == 'cart-address':
            FSM.state_cart_address_point(member, message)
        elif member['state'] == 'order-message':
            FSM.state_message(member, message, True)
    return True
#   =========================================================================================
#                                         DEBUG RUNNING
#   =========================================================================================
if __name__ == '__main__':
    print("onchapline project... starting")

    offset = 0
    while True:
        url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/getUpdates?offset={0}'.format(offset+1)

        content = requests.get(url).content.decode("utf-8")
        jsonResult = json.loads(content)
        messageList = jsonResult['result']
        for message in messageList:
            if int(message['update_id']) > offset:
                offset = int(message['update_id'])
            if 'message' in message:

                if 'text' in message['message']:
                    memberId = message['message']['chat']['id']
                    messageText = message['message']['text']
                    member = {
                        '_id'  : memberId,
                        'name' : 'null',
                        'state': 'null',
                        'state_extra': {}
                    }
                    for m in collections['members'].find({"_id" : memberId}):
                        member = m
                    
                    print("{1}> {0}".format(messageText, member['name']))
                    FSMResult = FSMInput(member, messageText)

                if ('document' in message['message']) or ('audio' in message['message']) or ('photo' in message['message']) or ('video' in message['message']) or ('voice' in message['message']) or ('contact' in message['message']):
                    memberId = message['message']['chat']['id']
                    messageObject = message['message']
                    member = {
                        '_id'  : memberId,
                        'name' : 'null',
                        'state': 'null',
                        'state_extra': {}
                    }
                    for m in collections['members'].find({"_id" : memberId}):
                        member = m
                    
                    print("{1}> {0}".format('[file]', member['name']))
                    FSMResult = FSMInput(member, messageObject)
            elif 'callback_query' in message:
                memberId = message['callback_query']['from']['id']
                messageText = message['callback_query']['data']

                member = {
                        '_id'  : memberId,
                        'name' : 'null',
                        'state': 'null',
                        'state_extra': {}
                    }
                for m in collections['members'].find({"_id" : memberId}):
                    member = m

                print("{1}> {0}".format(messageText, member['name']))
                FSMResult = FSMInput(member, messageText)
        sleep(1)

    
