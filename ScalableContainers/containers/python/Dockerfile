FROM python:3.7-alpine

# Add core OS requirements
RUN apk update && apk add bash vim

# Add Python Libraries
RUN pip install pika

ADD  fill_queue.py /

