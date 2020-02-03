#!/usr/bin/env python
import pika
import sys
import os
import json

ROOT="/images"
rLen = len(ROOT)
classes = ('airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
HOSTNAME="sa_rabbitmq"

# Determine the expected category by parsing the directory (after the root path)
def fnameToCategory(fname):
    for c in classes:
        if (fname.find(c) > rLen):
            return (classes.index(c))
    return -1 # This should never happen

IMGS=[]
for root, dirs, files in os.walk(ROOT):
    for filename in files:
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            fullpath=os.path.join(root, filename)
            cat = fnameToCategory(fullpath)
            data = {
                "image" : fullpath,
                "category": cat,
                "catName": classes[cat]
            }
            message = json.dumps(data)
            IMGS.append(message)

connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOSTNAME))
channel = connection.channel()

channel.queue_declare(queue='image_queue', durable=True)

print("Number of Images = ", len(IMGS))

for i in IMGS:
    channel.basic_publish( exchange='', routing_key='image_queue', body=i,
        properties=pika.BasicProperties( delivery_mode=2,  )
    )
    print("Queued ", i)

connection.close()



