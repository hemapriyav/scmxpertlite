from pymongo import MongoClient



client = MongoClient("mongodb+srv://admin:admin@cluster0.pvu9p3x.mongodb.net/?retryWrites=true&w=majority")


db = client.scm

collection_name = db["users"]
collection_name2 = db["shipments"]
collection_name3 = db["device_data"]