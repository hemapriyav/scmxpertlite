from kafka import KafkaConsumer
from pymongo import MongoClient
from json import loads


# consumer = KafkaConsumer(
#     'scm_data',
#      bootstrap_servers=['localhost:9092'],
#      auto_offset_reset='earliest',
#      enable_auto_commit=True,
#      group_id='my-group',
#      value_deserializer=lambda x: loads(x.decode('utf-8')))

consumer = KafkaConsumer ('scm_data',bootstrap_servers = ['localhost:9092'],
value_deserializer=lambda m: loads(m.decode('utf-8')))

client = MongoClient("mongodb+srv://admin:admin@cluster0.pvu9p3x.mongodb.net/?retryWrites=true&w=majority")
collection = client.scm.device_data
count = 0
while True:
    for message in consumer:
        print("inside while loop consumer")
        # print(message.value[0])
        # message = message.value
        message = message.value[0]
        collection.insert_one(message)
        print(message)
        #print("after serialization - "+ str(device_data_serializer(message)))

