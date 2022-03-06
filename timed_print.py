"""Enhance print() with time prefixes (ala logging output)"""
import datetime
import time

# start our clock for elapsed_print()
_elapsed_start = time.perf_counter_ns()


def reset_elapsed_timer():
    global _elapsed_start
    _elapsed_start = time.perf_counter_ns()


def millis() -> int:
    """Emulate Arduino millis() function"""
    return (time.perf_counter_ns() - _elapsed_start) // 1000000


def elapsed_print(*args):
    """print(*args) prefixed by elapsed run time as SSS.uuu """
    elapsed_secs = millis() / 1000
    print(f'{elapsed_secs:07.3f}', *args)


def hms_print(*args):
    """print(*args) prefixed by current time as HH:MM:SS.uuu """
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(now, *args)
