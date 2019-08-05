# coding=utf8



import datetime
import threading


class Window(object):

    def __init__(self):
        self.lock = threading.RLock()
        self.total_number = 0
        self.error_number = 0
        self.created_time = datetime.datetime.now()

    def incr_error(self):
        self.lock.acquire()
        self.total_number += 1
        self.error_number += 1
        self.lock.release()
        return self.total_number, self.error_number
        
    def incr_normal(self):
        self.lock.acquire()
        self.total_number += 1
        self.lock.release()
        return self.total_number, self.error_number

    @property
    def error_ratio(self):
        self.lock.acquire()
        if not self.total_number:
            self.lock.release()
            return 0.0
        ret = self.error_number / float(self.total_number)
        self.lock.release()
        return ret


class Counter(object):

    def __init__(self, interval=100, threshold=0.5):
        self.interval = interval
        self.threshold = threshold
        self.window = Window()
        self.lock = threading.RLock()

    def _reset_window(self):
        del self.window
        self.window = Window()

    @property
    def current_window(self):
        return self.window or Window()

    @property
    def error_ratio(self):
        return self.current_window.error_ratio

    def incr_error(self):
        return self.current_window.incr_error()

    def incr_normal(self):
        return self.current_window.incr_normal()

    def is_available(self):
        self.lock.acquire()
        now = datetime.datetime.now()
        delta = now - self.current_window.created_time
        if delta.seconds < self.interval:
            # FIXME: not clear right here?
            self.lock.release()
            return True

        if self.error_ratio >= self.threshold:
            self._reset_window()
            self.lock.release()
            return False

        self._reset_window()
        self.lock.release()
        return True


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
        print(process.memory_info().rss, \
                c.window.error_ratio, c.window.error_number, c.window.total_number)
        print(c.is_available())
        print('-> run next test')





