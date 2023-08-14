from kafka import KafkaConsumer
from pymongo import MongoClient
from json import loads
import os
from dotenv import load_dotenv
# load_dotenv(dotenv_path=".env")
load_dotenv()

boot_server = os.getenv('BOOT_SERVER')
print(boot_server)
# boot_server = "kafka"

consumer = KafkaConsumer (os.getenv('TOPIC'),bootstrap_servers = boot_server,
value_deserializer=lambda m: loads(m.decode('utf-8')))

# consumer = KafkaConsumer ('scm_data',bootstrap_servers = ['localhost:9092'],
# value_deserializer=lambda m: loads(m.decode('utf-8')))

client = MongoClient(os.getenv("CONNECTION_STRING"))
database = os.getenv("DATABASE")
db = client.get_database(database)
collection=db[str(os.getenv("DEVICE_DATA_COLLECTION"))]

# client = MongoClient("mongodb+srv://admin:admin@cluster0.pvu9p3x.mongodb.net/?retryWrites=true&w=majority")
# collection = client.scm.device_data
count = 0
while True:
    for message in consumer:
        print("inside while loop consumer")
        message = message.value[0]
        collection.insert_one(message)
        print(message)

