import context

import read_config as rc
import database

rc.config_init('../monitor.conf')
PSQL_CONFIG = rc.read_section(rc.CONFIG_ID_POSTGRESQL)
print(PSQL_CONFIG)

conn = database.connection(PSQL_CONFIG)
cur = conn.cursor()
cur.execute("SELECT * FROM sites;")

for i in cur.fetchall():
    print(i)

cur.close()
conn.close()
