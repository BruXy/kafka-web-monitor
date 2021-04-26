"""
PostreSQL Handling functions
============================
"""

import psycopg2
from psycopg2.extras import NamedTupleCursor
import read_config as rc


def connection(config):
    """Establish PostgreSQL connection.

    :type config: dict
    :param confg: dictionary with configuration:

      {
        'host': '',
        'port': '',
        'user': '',
        'password': '',
        'database': '',
        'sslmode': 'require'
      }

    :return: connection object

    """
    connection = None
    try:
        connection = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['database'],
            user=config['user'],
            password=config['password'],
            sslmode=config['sslmode'],
            cursor_factory=NamedTupleCursor
        )
    except Exception as err:
        print("Error: Unable to connect to PostgreSQL: ", config['host'])
        quit(1)

    return connection

