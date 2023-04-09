import json
from kafka import KafkaConsumer
from random import randint


consumer = KafkaConsumer(bootstrap_servers=["127.0.0.1:54351"], group_id="demo-group",
                         auto_offset_reset="earliest", enable_auto_commit=False,
                         consumer_timeout_ms=1000, 
                         value_deserializer=lambda m: json.loads(m.decode('ascii')))

while True:
    subscription_order_id = randint(1, 3)
    subscription_topic = str(subscription_order_id)
    consumer.subscribe(subscription_topic)
    try:
        for message in consumer:
            topic_info = f"topic: {message.partition}|{message.offset})"
            message_info = f"key: {message.key}, {message.value}"
            print (f"{topic_info}, {message_info}")
            print ('\n')
    except Exception as e:
        print (f"Error occurred while consuming messages: {e}")
    finally:
        consumer.close()
        break
