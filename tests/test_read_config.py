import context

import read_config as rc

# 1. Read websites' settings

expected = {
    't1': {
        'url': 't1',
        'period': '60',
        'html_regex': 'product',
        'connect_timeout': '3',
        'read_timeout': '30',
    },
    't2': {
        'url': 't2',
        'period': '30',
        'html_regex': '',
        'connect_timeout': '3',
        'read_timeout': '30',
    }
}

rc.config_init('test-monitor.conf')
retval = rc.config_websites()
print(retval)
print(expected)

assert retval == expected

# 2. Check for missing global configuration

expected = 'Error: Missing "global-kafka" configuration section!'

try:
    rc.config_init('test-monitor-err.conf')
except Exception as e:
    print(str(e) + '\n' + expected)
    assert str(e) == expected
