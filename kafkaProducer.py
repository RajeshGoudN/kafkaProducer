import logging
import os
import requests
import json
from confluent_kafka import Producer


producer = None  # Global producer object


def connecting_to_kafka():
    global producer
    try:
        logging.info("Defining Confluent configuration")

        conf = {
            'bootstrap.servers': 'pkc-619z3.us-east1.gcp.confluent.cloud:9092',
            'security.protocol': 'SASL_SSL',
            'sasl.mechanism': 'PLAIN',
            'sasl.username': "VQQPMEBGHFUEJBJL",
            'sasl.password': "OuBjm+YIYB/p846Su/ZQadTHMQCFppc/ve5Y+crraWKw+6hhET9BLitK+kdENLNd"
        }

        logging.info("Creating Kafka producer")
        producer = Producer(conf)
        logging.info("Kafka producer successfully created")
    except Exception as e:
        logging.error(f"Unable to establish connection because {e}")


def fetch_data_from_api():
    global producer
    try:
        logging.info("Fetching data from API")
        response = requests.get("https://api.restful-api.dev/objects")
        
        if response.status_code != 200:
            logging.error(f"API returned an error status: {response.status_code}")
            return

        jsonData = response.json()

        for item in jsonData:
            id = str(item.get("id", "default_key"))
            value = json.dumps(format_response(item))
            
            producer.produce(
                topic="latest_updated_data",
                key=id,
                value=value,
                callback=delivery_report
            )
            producer.flush()
            logging.info(f"Sent data to Kafka: key={id}, value={value}")
    except Exception as e:
        logging.error(f"Unable to fetch data from API: {e}")


def format_response(item):
    """
    Formats the API response item for Kafka.
    Modify this function based on your specific requirements.
    """
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "data": item.get("data"),
    }


def delivery_report(err, msg):
    """
    Callback for message delivery reports.
    """
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")


file_path = "log.txt"

if __name__ == "__main__":
    logging.basicConfig(
        filename=file_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Calling Kafka connection method")
    connecting_to_kafka()

    if producer is not None:
        fetch_data_from_api()
    else:
        logging.error("Kafka producer is not initialized")
