import socket
from kafka import KafkaProducer
from json import dumps

import os
from dotenv import load_dotenv

load_dotenv()

# test = os.getenv('test')

# print(test)


# PORT = 5050
PORT = int(os.getenv('PORT'))

# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "scmxpertlite-server-1"

# SERVER = "root-server-1"
SERVER = os.getenv('SERVER')

print(SERVER)

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((SERVER,PORT))

# topic_name = "scm_data"
topic_name = os.getenv('TOPIC')

# boot_server = "kafka"
boot_server = os.getenv('BOOT_SERVER')

producer = KafkaProducer(bootstrap_servers=boot_server,api_version=(0,11,5))
# producer = KafkaProducer(bootstrap_servers=['localhost:9092'],api_version=(0,11,5))

count = 0
while (count < 15):
 print("inside while loop producer - "+ str(count))
 data = c.recv(1024)
 print(data)
 producer.send(topic_name,data)
 count = count + 1

c.close()


