# Tubbe

## What ?

Tubbe是一个定义了统一降级处理流程的库，适用于任何远程，服务接口，函数的调用，提供了两层降级:

* 正常->异常
* 异常->缓存



## Todo

* metrics collector
* circuit breaker


## Get Started

```python
    import time
    import logging

    from gevent import monkey
    monkey.patch_all()

    from tubbe.command import BaseAsyncCommand, BaseSyncCommand

    #class PowCommand(BaseSyncCommand):
    class PowCommand(BaseAsyncCommand):

        def run(self, n):
            raise Exception('a')
            return pow(n, 2)

        def fallback(self, n):
            time.sleep(3)
            return pow(n, 3)

        def cache(self, n):
            return pow(n, 4)

    logger = logging.getLogger(__name__)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('/tmp/tubbe.log')
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    c = PowCommand('pow', timeout=2, logger=logger)
    print c.execute(3)
```
