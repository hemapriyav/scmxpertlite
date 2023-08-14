from kafka import KafkaConsumer
from pymongo import MongoClient
from json import loads
import os
from dotenv import load_dotenv

### Loads the env variables
load_dotenv()

boot_server = os.getenv('BOOT_SERVER')
print(boot_server)

### Creates Consumer 
consumer = KafkaConsumer (os.getenv('TOPIC'),bootstrap_servers = boot_server,
value_deserializer=lambda m: loads(m.decode('utf-8')))

# consumer = KafkaConsumer ('scm_data',bootstrap_servers = ['localhost:9092'],
# value_deserializer=lambda m: loads(m.decode('utf-8')))

### Establishes connection with DB and gets the database and collection
client = MongoClient(os.getenv("CONNECTION_STRING"))
database = os.getenv("DATABASE")
db = client.get_database(database)
collection=db[str(os.getenv("DEVICE_DATA_COLLECTION"))]

### Reads data from Producer and stores it in DB
while True:
    for message in consumer:
        message = message.value[0]
        collection.insert_one(message)

