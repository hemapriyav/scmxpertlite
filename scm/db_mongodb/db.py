

import os
from dotenv import load_dotenv

from pymongo import MongoClient
# load_dotenv(dotenv_path=".env")
load_dotenv()
# boot_server = os.getenv('boot_server')
# print(boot_server)

# test = os.getenv('test')
# print(test)

# load_dotenv()

print("inside db")

# conn_string = os.getenv('CONNECTION_STRING')
# print(conn_string)
#client = MongoClient("mongodb+srv://admin:admin@cluster0.pvu9p3x.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(os.getenv("CONNECTION_STRING"))

#db = client.scm
print(os.getenv("DATABASE"))
database = os.getenv("DATABASE")
db = client.get_database(database)

# collection_name = db["users"]
# collection_name2 = db["shipments"]
# collection_name3 = db["device_data"]

collection_name = db[str(os.getenv("USER_COLLECTION"))]
collection_name2 = db[str(os.getenv("SHIPMENT_COLLECTION"))]
collection_name3 = db[str(os.getenv("DEVICE_DATA_COLLECTION"))]