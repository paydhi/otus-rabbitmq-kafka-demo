import sys
import time

import pika

name = sys.argv[1] if len(sys.argv) > 1 else "C1"

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
ch = conn.channel()
ch.queue_declare(queue="queue-any", durable=True)
ch.basic_qos(prefetch_count=1)

def on_message(c, method, props, body):
    print(name, "got", body.decode())
    time.sleep(1)
    c.basic_ack(method.delivery_tag)

ch.basic_consume(queue="queue-any", on_message_callback=on_message)
print(name, "waiting for messages, Ctrl+C to stop")
ch.start_consuming()