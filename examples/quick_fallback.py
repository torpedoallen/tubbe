# coding=utf8


import logging

from tubbe.command import BaseSyncCommand
from tubbe.circuit_breaker import SwitchCircuitBreaker


class DemoCommand(BaseSyncCommand):

    def run(self):
        return 1

    def fallback(self):
        return 2

    def cache(self):
        return 3

    def validate(self, result):
        return True


logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.INFO)
handler = logging.FileHandler('/tmp/tubbe.log')
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)



command = DemoCommand('demo_test', timeout=1, logger=logger,
                            circuit_breaker_class=SwitchCircuitBreaker)


# NOTE: 如果是本地需要起switch服务，否则默认不熔断
# NOTE: 如果是生产环境需要保证switch项已经创建，否则默认不熔断
print command.execute()
