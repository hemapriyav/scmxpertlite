

import os
from dotenv import load_dotenv

from pymongo import MongoClient

### Loads the env variables
load_dotenv()

### Connects with Mongo DB using the connection string
client = MongoClient(os.getenv("CONNECTION_STRING"))

### Gets the database
database = os.getenv("DATABASE")
db = client.get_database(database)

### Gets the required collections from the database
user_collection = db[str(os.getenv("USER_COLLECTION"))]
shipment_collection = db[str(os.getenv("SHIPMENT_COLLECTION"))]
device_data_collection = db[str(os.getenv("DEVICE_DATA_COLLECTION"))]