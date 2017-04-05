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

collections = {}
debug = False

def init(clc):
    global collections
    collections = clc

def acceptCart(member):
    address = member['state_extra']['address']
    for i in range(0, len(member['cart'])):
        member['cart'][i]['status'] = 'IN-PROGRESS'

    cart = {
        'address' : address,
        'sender'  : member,
        'orders'  : member['cart'],
        'status'  : 'IN-PROGRESS'
    }

    cartId = collections['orders'].insert(cart)
    cart['_id'] = cartId
    collections['members'].update({'_id': member['_id']}, {'$set': {'cart': []}})
    sendOrderSentMessage(cart)

def sendOrderSentMessage(cart):
    for i in range(0, len(cart['orders'])):
        Telegram.orderForPrint(cart, i)