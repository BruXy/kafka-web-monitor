kafka-web-monitor
=================

Author: Martin 'BruXy' Bruchanov

HTTP(S) monitoring tool
-----------------------

This is a website monitoring tool using Apache Kafka messaging framework.

* `producer.py` collects metrics and sends them via Kafka to
* `consumer.py` which stores the received message to the PostgreSQL database.

To run producer/customer use (exit with `Ctrl-c`):

```
./producer.py monitor.conf
./consumer.py monitor.conf
```

A configuration example can be found in:
[example_monitor.conf](example_monitor.conf).

**Overview:**

_Producer_ is using `src/https_status.py` to check website metrics in defined
period. It collects:

* timestamp,
* GET status/errors,
* website response time and
* optionally tests if the page HTML contains text defined by regex.

If there is a TCP connection error when requesting some URL, the status metric
and response time is set to 0. Timeouts for TCP and HTTP can be set in the
configuration file.

Each website monitor runs in a separate thread and sends collected
metric to Apache Kafka.

_Consumer_ receives messages from Apache Kafka and stores them in a PostgreSQL
database. Each monitoring stream is saved to a separate database table. All
methods for database queries are defined in `src/database.py`.

Both scripts are using `src/read_config.py` to parse text configuration file.

Installation
------------

1. Clone repository: `git clone https://github.com/BruXy/kafka-web-monitor.git`.
2. If necessary for executing a new Python virtual environment, there is
   `make venv` to setup a local environment in `PYTHON_VENV_DIR`
   as defined in the `Makefile`.
3. Install required packages: `make pip-install`

Development
-----------

Check `Makefile` for additional support tools. To use a PostreSQL database you
need to have `postgres` (`psql`) client and `libpq-devel` installed, use `make
dev-install` to add these packages on RPM based GNU/Linux distributions.

Code syntax check and unit tests can be executed by invoking `make` without any
parameters, recipes for these tests are defined in target "syntax" and "test".

