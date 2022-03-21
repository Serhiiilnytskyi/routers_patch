import os
import requests
import json
import html
import csv
import argparse
import traceback

from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from zte_H118N import zte_H118N
from zte_F670 import zte_F670
from shared import *

os.makedirs('saves', exist_ok=True)

patchers = {
    'ZXHN H118N /// Mini web server 1.0 ZTE corp 2005.': zte_H118N,
    'F670 /// Mini web server 1.0 ZTE corp 2005.': zte_F670
}

def lookup_target(target, just_look=True):
    if isinstance(target, str):
        if (target := parse_target(target)) is None:
            return None

    s = requests.Session()
    s.hooks = { 'response': lambda r, *args, **kwargs: r.raise_for_status() }
    s.headers.update({
        'User-Agent': random.choice(useragents),
        'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3'
    })

    try:
        res = s.get(f'http://{target.ip}', timeout=TIMEOUT)

        target.server = res.headers.get('Server', '')
        target.date = res.headers.get('Date', '')

        if (match_title := re.search(r'<title>(.*)</title>', res.text)) is not None:
            title = match_title.group(1)
            target.title = html.unescape(title)

        with open(f'saves/{target.ip}.html', 'w') as f:
            f.write(res.text)

        with open(f'saves/{target.ip}.headers', 'w') as f:
            json.dump(dict(res.headers), f)

        if target.status == Status.Success:
            target.status = Status.Patched

        if just_look or target.status == Status.Patched:
            return target

        for fingerprint, patcher in patchers.items():
            if fingerprint == f'{target.title} /// {target.server}':
                print(f'---> {target} with {fingerprint}')
                target.status = patcher(target)
                print(f'<--- {target} with {fingerprint}')
                return target

        target.status = Status.WrongTarget
        return target

    except (requests.exceptions.ReadTimeout, requests.RequestException):
        if target.status not in (Status.Success, Status.Patched):
            target.status = Status.Inaccessible

        return target

    except Exception as exception:
        print(traceback.format_exc())

        if target.status not in (Status.Success, Status.Patched):
            target.status = Status.Inaccessible
        return target

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'targetsfile'
    )

    parser.add_argument(
        '--just-look',
        action='store_true',
        default=False,
        help='Collect index, no patching'
    )

    parser.add_argument(
        '-t',
        '--threads',
        type=int,
        default=216
    )
    return parser

if __name__ == '__main__':
    args = init_argparse().parse_args()

    with open(args.targetsfile) as f:
        targets = f.read().split('\n')
        targets.insert(0, '')

    indexfile = f'{args.targetsfile.rsplit(".", 1)[0]}-index.csv'
    with open(indexfile, 'w') as f:
        header = list(Target.__dict__['__annotations__'].keys()) + ['repr']
        csv.writer(f).writerow(header)

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {}

        for index, target in enumerate(targets):
            future = pool.submit(lookup_target, target, args.just_look)
            futures[future] = index

        tbar = tqdm(as_completed(futures), total=len(targets))
        for future in tbar:
            index = futures[future]

            try:
                target = future.result()
                tbar.set_description(repr(target))

                if target:
                    target.index = index

                    with open(indexfile, 'a') as f:
                        csv.writer(f).writerow(target.to_list())

            except Exception:
                print(traceback.format_exc())
