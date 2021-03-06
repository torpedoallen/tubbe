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
# NOTE: 如果是生产环境需要保证switch项已经创建，否则默认不熔断, 上线前一定要保证switch已经创建
# NOTE: switch item名称和Command保持一致，field名为toggle，类型bool，True为熔断，False为不熔断,
#       get_switch_info 返回值样例 {'toggle': True}
import time
print command.execute()
from switch_client.local_cache import lc
time.sleep(9.9)
print lc.dataset
print lc.get('demo_test')
print command.execute()
print lc.dataset
print lc.get('demo_test')
time.sleep(1)
print lc.dataset
print lc.get('demo_test')
