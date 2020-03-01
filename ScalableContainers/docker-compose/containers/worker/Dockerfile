FROM ubuntu

RUN apt-get update 
RUN apt-get install -y python3 python3-pip 

RUN pip3 install --upgrade mxnet gluoncv pika 
RUN pip3 install psycopg2-binary 

# Add worker logic necessary to process queue items
ADD  worker.py /

# Start the worker
CMD ["python3", "./worker.py" ]

