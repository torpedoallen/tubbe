# coding=utf8



import datetime
import threading


class Window(object):

    def __init__(self):
        self.lock = threading.RLock()
        self.total_number = 0
        self.error_number = 0
        self.created_time = datetime.datetime.now()

    def incr_total_number(self):
        self.lock.acquire()
        self.total_number += 1
        self.lock.release()
        
    def incr_error_number(self):
        self.lock.acquire()
        self.error_number += 1
        self.lock.release()

    @property
    def error_ratio(self):
        if not self.total_number:
            return 0.0
        return self.error_number / float(self.total_number)


class Counter(object):

    def __init__(self, interval=100, threshold=0.5):
        self.interval = interval
        self.threshold = threshold
        self.window = Window()
        self.lock = threading.RLock()

    def _reset_window(self):
        del self.window
        self.window = Window()

    def is_available(self):
        self.lock.acquire()
        now = datetime.datetime.now()
        delta = now - self.window.created_time
        print delta, self.interval
        if delta.seconds < self.interval:
            # FIXME: not clear right here?
            self.lock.release()
            return True

        if self.window.error_ratio >= self.threshold:
            self._reset_window()
            self.lock.release()
            return False

        self._reset_window()
        self.lock.release()
        return True

    def handle_income(self):
        self.lock.acquire()
        self.window.incr_total_number()
        self.lock.release()

    def handle_error(self):
        self.lock.acquire()
        self.window.incr_error_number()
        self.lock.release()


if __name__ == "__main__":
    import time
    import random
    import os
    import psutil
    process = psutil.Process(os.getpid())


    c = Counter(interval=10) # 10 secs
    for _ in range(10):
        for i in range(90): # 90 and 100
            c.handle_income()
            time.sleep(0.1)
            if random.randrange(2):
                c.handle_error()
        print process.memory_info().rss, \
                c.window.error_ratio, c.window.error_number, c.window.total_number
        print c.is_available()
        print '-> run next test'





