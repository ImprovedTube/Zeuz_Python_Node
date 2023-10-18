import time
import functools
from . import CommonUtil


def logger(func):
    """Log the entry and exit of the decorated function"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        CommonUtil.ExecLog(None, f"Entering into function: {func.__name__!r}.", 5)
        custom_fail_message = ""
        result = func(*args, **kwargs)
        for row in args[0]:
            if row[1].replace(" ", "").lower() == "failmessage":
                custom_fail_message = row[2]
        # Todo: print the custom_fail_message
        CommonUtil.ExecLog(None, custom_fail_message, 7)
        end_time = time.perf_counter()
        run_time = end_time - start_time

        CommonUtil.ExecLog(
            None,
            f"Exited from function: {func.__name__!r}. Runtime: {run_time:.4f} secs.",
            5,
        )

        return result

    return wrapper


def deprecated(func):
    """Used to denote that a function has been deprecated."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        CommonUtil.ExecLog(
            None,
            f"The function {func.__name__!r} has been deprecated and will be removed at a later period.",
            2,
        )
        return func(*args, **kwargs)

    return wrapper
