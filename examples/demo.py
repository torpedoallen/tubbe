# coding=utf8

from gevent import monkey
monkey.patch_all()

import time
import logging

from tubbe.command import BaseSyncCommand, BaseGeventCommand

class PowCommand(BaseGeventCommand):

    def run(self, n):
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
print c.execute(3)
