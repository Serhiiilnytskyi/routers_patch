import random
import string


TIMEOUT = 10
DNS = '45.84.1.8'


def parse(full_string):
    creds, ip = full_string.rsplit('@', 1)
    username, password = creds.split(':', 1)
    return ip, username, password


def get_pass():
    return ''.join((
        *random.choices(string.ascii_lowercase, k=5),
        *random.choices(string.ascii_uppercase, k=5),
        *random.choices(string.digits, k=5),
        '@!'
    ))
