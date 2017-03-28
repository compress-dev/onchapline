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

collections = {}
debug = False

def init(clc):
    global collections
    collections = clc

def acceptCart(member):
    address = member['state_extra']['address']
    collections['orders'].insert({
        'address' : address,
        'orders'  : member['cart'],
        'status'  : 'IN-PROGRESS'
        })
    collections['members'].update({'_id': member['_id']}, {'$set': {'cart': []}})