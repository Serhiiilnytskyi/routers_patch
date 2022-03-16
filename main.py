import traceback
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor

from fast_1744 import rostelekom_fast_1744
from zte_F670 import zte_F670
from zte_H118N import zte_H118N


def run(targets):
    with ThreadPoolExecutor(max_workers=100) as ex:
        futures = []
        for method in [rostelekom_fast_1744, zte_F670, zte_H118N]:
            futures.extend([ex.submit(method, target) for target in targets])

        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                print(traceback.format_exc())
