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
    print(member)
    if member['state'] == 'null':
        FSM.stateNull(member, message)
    elif member['state'] == 'reg0':
        FSM.state_reg0(member, message)
    elif member['state'] == 'ready':
        FSM.state_ready(member, message)
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
                memberId = message['message']['chat']['id']
                messageText = message['message']['text']
                member = {
                    '_id'  : memberId,
                    'name' : 'null',
                    'state': 'null'
                }
                for m in collections['members'].find({"_id" : memberId}):
                    member = m
                
                print("{1}> {0}".format(messageText, member['name']))
                FSMResult = FSMInput(member, messageText)

        sleep(1)

    
