import pika, sys

count = int(sys.argv[1]) if len(sys.argv) > 1 else 5

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
ch = conn.channel()
ch.queue_declare(queue="queue-any", durable=True)

for i in range(count):
    ch.basic_publish(exchange="", routing_key="queue-any", body=f"msg {i}".encode())
    print("sent", i)

conn.close()