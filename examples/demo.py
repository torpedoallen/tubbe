# coding=utf8


import gevent
from gevent import monkey
monkey.patch_all()

import time
import logging
import random

from tubbe.command import BaseSyncCommand, BaseGeventCommand

class PowCommand(BaseGeventCommand):

    def run(self, n):
        if random.randrange(2):
            raise Exception('a')
        return pow(n, 2)

    def fallback(self, n):
        time.sleep(3)
        with open('/tmp/aa', 'w+') as f:
            f.write('close')
        return pow(n, 3)

    def cache(self, n):
        return pow(n, 4)

    def validate(self, result):
        return True

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/tmp/tubbe.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

c = PowCommand('pow', timeout=2, logger=logger)
tasks = [gevent.spawn(c.execute, i%4) for i in xrange(1000)]
gevent.joinall(tasks)
time.sleep(5)
tasks = [gevent.spawn(c.execute, i%4) for i in xrange(1000)]
gevent.joinall(tasks)
