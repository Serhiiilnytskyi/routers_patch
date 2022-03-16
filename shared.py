import random
import string
import toml
import re
import html

from enum import Enum

class Status(Enum):
    Inaccessible = 0
    TryAgain = 1
    WrongAuth = 2
    WrongTarget = 3
    PartialSuccess = 4
    Success = 5

locals().update(toml.load('config.toml'))
TIMEOUT = 20

with open('useragents.txt') as f:
    useragents = f.read().split('\n')

def parse(full_string):
    creds, ip = full_string.rsplit('@', 1)
    username, password = creds.split(':', 1)
    return ip, username, password

def parse_target(target):
    if len(target) == 0 or not '@' in target:
        return None

    try:
        target, status = target.rsplit(',', 1)
        auth, ip = target.rsplit('@', 1)
        username, password = auth.split(':', 1)

        return ip, username, password, status[0]
    except:
        return None

def fingerprint(res):
    if (match_title := re.search(r'<title>(.*)</title>', res.text)) is not None:
        title = match_title.group(1)
        title = html.unescape(title)
    else:
        title = ''

    server = res.headers.get('Server', '')
    return title + ' /// ' + server

def get_pass():
    return NEWPASS
