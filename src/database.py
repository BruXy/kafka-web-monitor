"""
PostreSQL Handling functions
============================

"""

import psycopg2
from psycopg2.extras import NamedTupleCursor

# Storing of sites, primary key is configuration section id

TABLE_SITES = """
CREATE TABLE IF NOT EXISTS sites (
    url VARCHAR NOT NULL,
    storage VARCHAR NOT NULL,
    PRIMARY KEY (storage)
);
"""

# Insert record to sites, update URL when changed in the config

TABLE_SITES_RECORD = """
INSERT INTO sites (url, storage) VALUES (%s, %s)
ON CONFLICT (storage) DO UPDATE SET url = %s;
"""

# Each site will have separate table for the log storage

TABLE_LOGS = """
CREATE TABLE IF NOT EXISTS {} (
    id SERIAL PRIMARY KEY,
    site_id varchar NOT NULL,
    FOREIGN KEY (site_id) REFERENCES sites(storage),
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    http_status SMALLINT NULL,
    response_time_ms INTEGER NULL,
    regex_match BOOLEAN NULL -- FALSE not matched, TRUE matched, NULL check was disabled
);
"""

# Monitoring record

INSERT_STATUS = """
INSERT INTO {} (site_id, time, http_status, response_time_ms, regex_match)
    VALUES(%s, %s, %s, %s, %s);
"""


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
    db_conn = None
    try:
        db_conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            dbname=config['database'],
            user=config['user'],
            password=config['password'],
            sslmode=config['sslmode'],
            cursor_factory=NamedTupleCursor
        )
        db_conn.autocommit = True
    except Exception as err:
        print("Error: Unable to connect to PostgreSQL: ", config['host'], err)
        sys.exit(1)

    return db_conn


def init(db_conn, db_cfg_list):
    """Create/update tables if they do not exist yet.

    :param db_conn: connection to the PostgreSQL
    :type db_conn: psycopg2 connection object
    :param db_list: unique ids of log storage tables
    :type db_list: list of strings
    """

    cursor = db_conn.cursor()
    # create main table with site list
    cursor.execute(TABLE_SITES)

    # update sites table and create tables for metrics storage
    for db, cfg in db_cfg_list.items():
        # insert/update sites
        cursor.execute(TABLE_SITES_RECORD, (cfg['url'], db, cfg['url']))
        # create log stream tables
        cursor.execute(TABLE_LOGS.format(db))

    db_conn.commit()
    cursor.close()


def insert_status(cursor, table, site_id,
                  timestamp, http_status, response_time_ms, regex_match):
    """Save monitoring record to the database.

        :param cursor: PostgreSQL cursor
        :type cursor: psycopg2 cursor object

        :param table: website string id
        :param timestamp:
        :param http_status:
        :param response_time_ms:
        :param regex_match:
    """

    query = INSERT_STATUS.format(table)
    data = (site_id, timestamp, http_status, response_time_ms, regex_match)
    cursor.execute(query, data)
