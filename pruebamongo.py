import pymongo
import datetime

client = pymongo.MongoClient("mongodb+srv://datainsitu:d4t41ns1tu*@pruebas-qnl35.mongodb.net/gasodomesticos")
db = client.gasodomesticos

post = {"date":datetime.datetime.now(),
        "temperatura1":25,
        "temperatura2":23,
        "humedad":65,
        "altitud":1400,
        "flujo aire":[5.,5.1,4.9,5.2,5.1],
        "flujo gas":[1.7,1.6,1.8,1.9,1.6],
        "potencia":[1200,1190,1203,1195,1201]}

posts = db.pruebas
post_id = posts.insert_one(post).inserted_id
print post_id
