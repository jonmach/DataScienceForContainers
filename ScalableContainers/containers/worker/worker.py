#!/usr/bin/env python

from mxnet import gluon, nd, image
from mxnet.gluon.data.vision import transforms
from gluoncv import utils
from gluoncv.model_zoo import get_model
import psycopg2
import pika
import time
import json

def predictCategory(fname):
    img = image.imread(fname)
    
    class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
    
    transform_fn = transforms.Compose([
        transforms.Resize(32), transforms.CenterCrop(32), transforms.ToTensor(),
        transforms.Normalize([0.4914, 0.4822, 0.4465], [0.2023, 0.1994, 0.2010])
    ])
    img = transform_fn(img)
    net = get_model('cifar_resnet110_v1', classes=10, pretrained=True)
    
    pred = net(img.expand_dims(axis=0))
    ind = nd.argmax(pred, axis=1).astype('int')
    print('The input picture is classified as [%s], with probability %.3f.'% 
          (class_names[ind.asscalar()], nd.softmax(pred)[0][ind].asscalar()))
    return ind.asscalar(), nd.softmax(pred)[0][ind].asscalar()
    
def InsertResult(connection, fname, category, prediction, prob):
    count=0
    try:
        cursor = connection.cursor()

        qry = """ INSERT INTO CATEGORY_RESULTS (FNAME, CATEGORY, PREDICTION, CONFIDENCE) VALUES (%s,%s,%s,%s)"""
        record = (fname, category, prediction, prob)
        cursor.execute(qry, record)

        connection.commit()
        count = cursor.rowcount
        
    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into category_results table", error)

    finally:
        cursor.close()
        return count

#
# Routine to pull message from queue, call classifier, and insert result to the DB
#
def callback(ch, method, properties, body):
    data = json.loads(body)
    fname = data['image']
    cat = data['category']
    print("Processing", fname)
    pred, prob = predictCategory(fname)
    if (logToDB == 1):
        count = InsertResult(pgconn, fname, int(cat), int(pred), float(prob))
    else:
        count = 1  # Ensure the message is ack'd and removed from queue
        
    if (count > 0):
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_nack(delivery_tag=method.delivery_tag)

logToDB=1    # Set this to 0 to disable storing data in the database

pgconn = psycopg2.connect(user="postgres", password="password", 
                          host="sa_postgres", port="5432", database="postgres")

connection = pika.BlockingConnection(pika.ConnectionParameters(host='sa_rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='image_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='image_queue', on_message_callback=callback)

channel.start_consuming()
