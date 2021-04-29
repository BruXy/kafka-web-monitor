"""
Kafka Producer
==============

https://help.aiven.io/en/articles/489572-getting-started-with-aiven-for-apache-kafka

"""
import re
from sys import exit
from datetime import datetime
from time import sleep
from json import dumps

from kafka import KafkaProducer
from kafka.errors import KafkaError

import read_config as rc
import https_status as http

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

        @param site_id: unique site_id (log stream)
        @type site_id: string
        @param status: return of https_status function
        @type status: tuple
        @rtype: string
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


def main():
    # Read configuration
    rc.config_init('monitor.conf')
    kafka_cfg = rc.read_section(rc.CONFIG_ID_KAFKA)
    host_list = rc.config_websites()
    if DEBUG:
        print(host_list)

    # Init KafkaProducer
    producer = producer_init(kafka_cfg)

    while True:
        for host, config in host_list.items():
            print("Host: ", host)
            print("Config: ", config)
            if config['html_regex']:
                ro = re.compile(config['html_regex'])
            else:
                ro = None

            # Message
            metric = http.url_status(config['url'],
                                     float(config['connect_timeout']),
                                     float(config['read_timeout']),
                                     ro)

            message = http_msg_format(host, metric)
            if DEBUG:
                print("Sending: ", message)
            producer.send(kafka_cfg['topic'], message.encode('ascii'))
        sleep(30)

    producer.flush()

    producer.close()


if __name__ == '__main__':
    main()
