import datetime
import gc
import timeit
from functools import wraps

from logger.custom_logging import log


def MeasureTime(f):
    @wraps(f)
    def _wrapper(*args, **kwargs):
        gcold = gc.isenabled()
        gc.disable()
        start_time = timeit.default_timer()
        try:
            result = f(*args, **kwargs)
        finally:
            elapsed = timeit.default_timer() - start_time
            if gcold:
                gc.enable()
            log('Function "{}": {}s'.format(f.__name__, elapsed))
        return result

    return _wrapper