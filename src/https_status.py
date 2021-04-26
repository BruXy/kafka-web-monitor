"""
Website status monitoring
=========================

"""

import requests
import re

_AGENT = 'Kafka-Web-Monitor/1.0'  # identify our requests in server logs


def html_regex(re_obj, html):
    """ Check if page contains given regex pattern.

    @param re_obj: compiled regular expression object
    @type re_obj: re.Pattern from re.compile
    @param html: page content
    @type html: string

    @return: True if matched, False
    @rtype: bool
    """
    return True if re_obj.search(html) else False


def url_status(url, connect_timeout, read_timeout, re_obj=None):
    """Connect to given URL and obtain monitoring metrics.

    @param url: URL
    @type url: string
    @param connect_timeout: network connection timeout
    @type connect_timeout: int, float
    @param read_timeout: HTTP(S) read timeout
    @type read_timeout: int, float

    @rtype: tuple (int, float, bool)
    @return: ( http_status, response_time, regex_match )

    When http_status == 0, there was network connection error
    or no response from the host.

    """

    response = None
    try:
        response = requests.get(url,
                                headers={
                                    'user-agent': _AGENT,
                                    #                'Accept': 'application/json'
                                },
                                timeout=(connect_timeout, read_timeout)
                                )
    except requests.exceptions.ConnectionError as e:
        print('Error: Connection to "{}" failed: {}'.format(url, e))

    if response:
        response_time = response.elapsed.microseconds * 1e-3
        http_status = response.status_code
        print('Time: {}ms'.format(response_time))
        print('Status: ', http_status)
        print('Content: ', response.content.decode())
        if re_obj:
            regex_match = html_regex(re_obj, response.text)
            print('Regex Match: ', regex_match)
    else:
        http_status = 0
        response_time = 0
        regex_match = None

    return (http_status, response_time, regex_match)
