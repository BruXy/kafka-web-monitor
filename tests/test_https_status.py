import context

from https_status import url_status
import re

connect_timeout = 3
read_timeout = 30

# 1. Status check

ro = re.compile(r'product', flags=re.IGNORECASE | re.MULTILINE)
url = 'https://ifconfig.co'
status, response, match = url_status(url, connect_timeout, read_timeout, ro)

assert status == 200 and match == True

# 2. Connection error

url = 'https://does-not-exists'
status, response, match = url_status(url, connect_timeout, read_timeout, ro)

assert status == 0
