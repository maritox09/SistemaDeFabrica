import pymongo

client = pymongo.MongoClient('localhost', 27017)

db = client.SistemaDeFabrica

x = db.test.insert_one({"sadsa":"dasdas"})

print(x.inserted_id)