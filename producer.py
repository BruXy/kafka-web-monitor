#!/usr/bin/env python
"""
Kafka Producer
==============

https://help.aiven.io/en/articles/489572-getting-started-with-aiven-for-apache-kafka

"""
import sys
import threading
import re

from datetime import datetime
from time import sleep
from json import dumps

from kafka import KafkaProducer
from kafka.errors import KafkaError

import src.read_config as rc
import src.https_status as http

DEBUG = True


def producer_init(config):
    """KafkaProducer initialization.
       https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html

        :param config: configuration parameters
        :type config: dictionary
        :rtype: KafkaProducer object
     """
    try:
        producer = KafkaProducer(
            bootstrap_servers=config['host'] + ':' + config['port'],
            security_protocol=config['security_protocol'],
            ssl_cafile=config['ssl_cafile'],
            ssl_certfile=config['ssl_certfile'],
            ssl_keyfile=config['ssl_keyfile'],
        )
    except KafkaError as err:
        print('Error: KafkaProducer:', err)
        sys.exit(1)

    return producer


def timestamp_now():
    """Return curremt time as PostgreSQL timestamp."""
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S.%f')


def http_msg_format(site_id, status):
    """Format collected status metric to serialized JSON.

        :param site_id: unique site_id (log stream)
        :type site_id: string
        :param status: return of https_status function
        :type status: tuple
        :rtype: string
    """
    stencil = {
        'site_id': site_id,
        'timestamp': timestamp_now(),
        'http_status': status[0],
        'response_time': status[1],
        'regex_match': status[2],
    }

    if DEBUG:
        print(stencil)

    return dumps(stencil)


def http_main_checker(kafka_cfg, host, config):
    """Cycle for HTTP(S) status checker, which will be used as thread.

    :param kafka_cfg: configuration parameters for Apache Kafka
    :type kafka_cfg: dictionary produced by 'read_section'
    :param host: host id/section id
    :type host: string
    :param config: host configuration
    :type config: dictionary

    """
    # Create regex object if requested
    if config['html_regex']:
        ro = re.compile(config['html_regex'])
    else:
        ro = None

    # Init KafkaProducer
    kafka_producer = producer_init(kafka_cfg)
    kafka_topic = kafka_cfg['topic']

    while True:
        # Check HTTP(S) status
        metric = http.url_status(config['url'],
                                 float(config['connect_timeout']),
                                 float(config['read_timeout']),
                                 ro)

        # Send message
        message = http_msg_format(host, metric)
        if DEBUG:
            print("Thread: ", host)
            print("Sending to topic {}: {}".format(kafka_topic, message))

        kafka_producer.send(kafka_topic, message.encode('ascii'))
        kafka_producer.flush()

        # Wait checking period (total time - request duration)
        sleep(float(config['period']) - metric[1] / 1000)


def main(argv):
    # Read configuration
    config_file = rc.parse_cli(argv)
    rc.config_init(config_file)
    kafka_cfg = rc.read_section(rc.CONFIG_ID_KAFKA)
    host_list = rc.config_websites()
    if DEBUG:
        print(host_list)

    print('Producer executed, press Ctrl-c to exit...')
    # Execute thread for each monitored host
    for host, config in host_list.items():
        thread = threading.Thread(target=http_main_checker, name=host,
                                  args=(kafka_cfg, host, config))
        thread.start()


if __name__ == '__main__':
    main(sys.argv)
