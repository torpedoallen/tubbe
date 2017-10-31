# Tubbe

## Tubbe是什么？

Tubbe是一个定义了统一降级处理流程的库，受Netflix的Hystrix启发，适用于任何远程，服务接口，函数的调用。


## 核心思路

1. 提供了两层降级:
    * 正常->异常
    * 异常->缓存

2. 提供了`validate`接口方法，由使用者判断返回值不符合预期时的做法

3. 以异常为触发降级的基点，系统定义了三种异常（可能会扩展）: `TubbeTimeoutException`, `TubbeCircuitBrokenException`, `TubbeValidationException`，用户抛出的预期内或预期外的异常都会触发降级

4. 目前`Command`都是同步类型的，未来考虑加入异步处理


## Todo

* metrics collector
* circuit breaker


## Get Started

```python
    # coding=utf8

    import time
    import logging

    from tubbe.command import BaseSyncCommand

    class PowCommand(BaseSyncCommand):

        def run(self, n):
            raise Exception('a')
            return pow(n, 2)

        def fallback(self, n):
            time.sleep(3)
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
```
