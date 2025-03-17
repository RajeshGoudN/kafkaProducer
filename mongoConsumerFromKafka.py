from pymongo import MongoClient
import logging
from confluent_kafka import Consumer

file_path = "log_mongodb.txt"
client = None
consumer = None

def insert_data_into_mongo():
    try:
        print("abc")
        data = client["my-db"]
        collections = data["users"]
        consumer.subscribe(['latest_updated_data'])
        while True:
            message = consumer.poll(1.0)  # Wait for 1 second
            if message is None:
                continue
            if message.error():
                logging.error(f"Kafka error: {message.error()}")
                continue
            record = message.value()
            logging.info(f"Message received: {record}")
            # Insert into MongoDB
            collections.insert_one({"message": record.decode('utf-8')})
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        if consumer:
            consumer.close()
        if client:
            client.close()

def connect_to_kafka():
    global consumer
    try:
        logging.info("Defining Confluent Kafka configuration")

        conf = {
            'bootstrap.servers': 'pkc-619z3.us-east1.gcp.confluent.cloud:9092',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': "VQQPMEBGHFUEJBJL",
            'sasl.password': "OuBjm+YIYB/p846Su/ZQadTHMQCFppc/ve5Y+crraWKw+6hhET9BLitK+kdENLNd",
            'group.id': "group12",
            'auto.offset.reset': 'latest'
        }

        consumer = Consumer(conf)
        logging.info("Kafka consumer created successfully")
    except Exception as e:
        logging.error(f"Unable to fetch consumer: {e}")
        consumer = None

def connect_to_mongo():
    global client
    try:
        client = MongoClient("mongodb://root:example@localhost:27017/?authSource=admin")
        if client:
            logging.info("Connected to MongoDB server")
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        client = None

if __name__ == "__main__":
    logging.basicConfig(
        filename=file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    try:
        mongo_client = connect_to_mongo()
        kafka_consumer = connect_to_kafka()
        insert_data_into_mongo()
    except Exception as main_exception:
        logging.error(f"Main execution error: {main_exception}")
    finally:
        if consumer:
            consumer.close()
        if client:
            client.close()
