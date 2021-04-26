import configparser

CONFIG_FILE = ''
CONFIG = None
CONFIG_ID_KAFKA = 'global-kafka'
CONFIG_ID_POSTGRESQL = 'global-postgres'


def config_init(config_file):
    """Read configuration file, check if Kafka and Postgres
       'global' sections are presented.

       :param config_file: Path to configuration file.
       :type config_file: string
    """
    global CONFIG
    CONFIG = configparser.ConfigParser()
    CONFIG.read(config_file)

    err = 'Error: Missing "{}" configuration section!'

    if CONFIG_ID_KAFKA not in CONFIG.sections():
        raise Exception(err.format(CONFIG_ID_KAFKA))

    if CONFIG_ID_POSTGRESQL not in CONFIG.sections():
        raise Exception(err.format(CONFIG_ID_POSTGRESQL))

    pass


def read_section(section):
    """Read [section] values from configuration file."""
    return dict(CONFIG[section])


def config_websites():
    # need only websites
    websites = (CONFIG.sections()).copy()
    websites.remove(CONFIG_ID_KAFKA)
    websites.remove(CONFIG_ID_POSTGRESQL)

    # Check for duplicate Ids
    if len(websites) != len(set(websites)):
        raise Exception('Duplicate websites sections!')
    else:
        web_list = dict()
        for section in websites:
            web_list[section] = read_section(section)
        return web_list
