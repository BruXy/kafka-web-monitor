#!/usr/bin/env python
"""
Kafka Consumer
==============

https://help.aiven.io/en/articles/489572-getting-started-with-aiven-for-apache-kafka

"""
import sys
from json import loads

from kafka import KafkaConsumer
from kafka.errors import KafkaError

import src.read_config as rc
import src.database as db

DEBUG = True
KAFKA_GROUP_ID = 'bruxy-topic'
KAFKA_CLIENT_ID = 'bruxy-consumer'

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
            client_id=KAFKA_CLIENT_ID,  # do I need this?
            group_id=KAFKA_GROUP_ID,
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

    db.insert_status(cursor, msg['site_id'], msg['site_id'],
                     msg['timestamp'],
                     msg['http_status'],
                     int(msg['response_time'] * 1000),
                     msg['regex_match'])


def main(argv):
    # Read configuration
    config_file = rc.parse_cli(argv)
    rc.config_init(config_file)
    cfg_kafka = rc.read_section(rc.CONFIG_ID_KAFKA)
    cfg_postgres = rc.read_section(rc.CONFIG_ID_POSTGRESQL)

    # PostreSQL initialization
    psql = db.connection(cfg_postgres)
    db.init(psql, rc.config_websites())
    db_cursor = psql.cursor()

    # KafkaConsumer, message reception
    kafka_consumer = consumer_init(cfg_kafka)

    print('Consumer executed, press Ctrl-c to exit...')
    while True:
        try:
            for msg in kafka_consumer:
                if DEBUG:
                    print("Received: {}".format(msg.value))
                message2db(db_cursor, msg.value)
        except KeyboardInterrupt:
            print('Exiting consumer...')
            # Clean up...
            kafka_consumer.commit()
            kafka_consumer.close()
            db_cursor.close()
            psql.close()
            sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
