from pymongo import MongoClient
import time
import requests
import json

memberId = '295735582'
product = {
        "id"      : "1212",
        "title"   : "product 0",
        "price"   : "25000",
        "deposit" : "22000",
        "amount"  : "1000",
        "score"   : "5.3",
        "image"   : "http://tse1.mm.bing.net/th?id=OIP.Vl7oimI6QVHQ_6v9h5MXhAEiEs&pid=15.1",
        "office"  : "office 0"
    }
message = '<a href="{3}">{0}</a> از {1}\nتیراژ: {2}تایی\nهزینه: {4}تومان({5} تومان بیعانه)\nامتیاز: {7}\nانتخاب محصول: /take_{6}'.format(
        product['image']
        , product['title']
        , product['office']
        , product['amount']
        , product['price']
        , product['deposit']
        , product['score']
        , product['id'])
url = 'https://api.telegram.org/bot373573330:AAG6GE-HiDo10VZe7JpMND666Jpdj-ZBp3g/sendMessage?parse_mode=HTML&chat_id=' + str(memberId) + '&text=' + message

allowedMessages = json.dumps(["message", "inline_query", "chosen_inline_result", "callback_query"])
url += '&allowed_updates=' + allowedMessages

response = requests.get(url)
print(response.content.decode("utf-8"))