import socket
from kafka import KafkaProducer
from json import dumps

import os
from dotenv import load_dotenv

### Loads the env variables
load_dotenv()

PORT = int(os.getenv('PORT'))
SERVER = os.getenv('SERVER')

# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "scmxpertlite-server-1"
# SERVER = "root-server-1"

### Establishes Connection with the server
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((SERVER,PORT))

topic_name = os.getenv('TOPIC')
boot_server = os.getenv('BOOT_SERVER')

### Creates Producer
producer = KafkaProducer(bootstrap_servers=boot_server,api_version=(0,11,5))

# producer = KafkaProducer(bootstrap_servers=['localhost:9092'],api_version=(0,11,5))

count = 0

### Receives data from server and producer sends the received data along with the topic name
while (count < 15):
 data = c.recv(1024)
 producer.send(topic_name,data)
 count = count + 1

c.close()


