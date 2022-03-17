import random
import string
import toml
import re
import html

from dataclasses import dataclass
from enum import Enum

class Status(Enum):
    Inaccessible = 0
    TryAgain = 1
    WrongAuth = 2
    WrongTarget = 3
    PartialSuccess = 4
    Success = 5
    Patched = 6

@dataclass
class Target:
    index: int = 0
    ip: str = ''
    username: str = ''
    password: str = ''
    title: str = ''
    server: str = ''
    date: str = ''
    status: Status = Status.TryAgain

    def __repr__(self):
        return f'{self.username}:{self.password}@{self.ip},{self.status}'

    def to_list(self):
        return list(map(str, self.__dict__.values())) + [repr(self)]

def parse_status(status):
    if status.startswith('Status.'):
        return Status.__dict__[status.split('.', 1)[-1]]

    if status[0] == '✅':
        return Status.Patched

    return Status.TryAgain

def parse_target(target):
    status = Status.TryAgain

    try:
        if ',' in target:
            target, status = target.rsplit(',', 1)
            status = parse_status(status)

        if '@' not in target:
            if '.' not in target:
                return None

            return Target(ip=target, status=status)

        auth, ip = target.rsplit('@', 1)
        username, password = auth.split(':', 1)

        return Target(ip=ip, username=username, password=password, status=status)

    except Exception as e:
        print(traceback.format_exc())
        return None

TIMEOUT = 20
locals().update(toml.load('config.toml'))

with open('useragents.txt') as f:
    useragents = f.read().split('\n')
