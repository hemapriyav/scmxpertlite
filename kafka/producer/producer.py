import socket
from kafka import KafkaProducer
from json import dumps

PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = "scmxpertlite-server-1"
SERVER = "root-server-1"
print(SERVER)

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((SERVER,PORT))
topic_name = "scm_data"
boot_server = "kafka"
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


