"""
Kafka Consumer
==============

https://help.aiven.io/en/articles/489572-getting-started-with-aiven-for-apache-kafka

"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError

import read_config as rc
import database as db
from sys import exit
from json import loads


def consumer_init(config):
    """KafkaConsumer initialization.
       https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html

        :param config: configuration parameters
        :type config: dictionary
        :rtype: KafkaConfumer object
     """
    try:
        consumer = KafkaConsumer(
            config['topic'],
            auto_offset_reset="earliest",
            bootstrap_servers=config['host'] + ':' + config['port'],
            client_id="bruxy-consumer",  # do I need this?
            group_id="bruxy-topic",
            security_protocol=config['security_protocol'],
            ssl_cafile=config['ssl_cafile'],
            ssl_certfile=config['ssl_certfile'],
            ssl_keyfile=config['ssl_keyfile'],
        )
    except KafkaConsumer as err:
        print('Error: KafkaConsumer: ', err)
        sys.exit(1)

    return consumer


def message2db(cursor, msg_bytes):
    """Parse and store message in the database.

        :param cursor: database cursor

        Message example:

        b'{"site_id": "ifconfig",
           "timestamp": "2021-04-28 23:27:55.471290",
           "http_status": 200,
           "response_time": 187.036,
           "regex_match": true}'
    """
    msg = loads(msg_bytes)

    if msg['regex_match'] == None:
        regex_match = 'NULL'
    else:
        regex_match = msg['regex_match']

    db.insert_status(cursor, msg['site_id'], msg['site_id'],
                     msg['timestamp'],
                     msg['http_status'],
                     int(msg['response_time'] * 1000),
                     regex_match)


def main():
    # Read configuration
    rc.config_init('monitor.conf')
    cfg_kafka = rc.read_section(rc.CONFIG_ID_KAFKA)
    cfg_postgres = rc.read_section(rc.CONFIG_ID_POSTGRESQL)

    # PostreSQL initialization
    psql = db.connection(cfg_postgres)
    db.init(psql, rc.config_websites())
    db_cursor = psql.cursor()

    # KafkaConsumer, message reception
    kafka_consumer = consumer_init(cfg_kafka)
    # Call poll twice. First call will just assign partitions for our
    # consumer without actually returning anything
    for _ in range(2):
        raw_msgs = kafka_consumer.poll(timeout_ms=1000)
        for tp, msgs in raw_msgs.items():
            for msg in msgs:
                print("Received: {}".format(msg.value))
                message2db(db_cursor, msg.value)

    #message2db(db_cursor, b'{"site_id": "ifconfig", "timestamp": "2021-04-28 23:27:55.471290", "http_status": 200, "response_time": 187.036, "regex_match": true}')
    # Commit offsets so we won't get the same messages again
    # Note: there should be also default autocommit every 5000ms '?'
    kafka_consumer.commit()
    # '?' do I need to close consumer explicitely?


if __name__ == "__main__":
    main()
