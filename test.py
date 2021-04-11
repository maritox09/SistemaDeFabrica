import pymongo

client = pymongo.MongoClient('localhost', 27017)

db = client.SistemaDeFabrica

user = db.usuarios.find_one({"usuario": "Mario"})

if user:
    print("SIIIUUUUU")
else:
    print("NOOOOUUUUU")