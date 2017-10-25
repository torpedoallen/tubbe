# Tubbe

## What

Tubbe is a latency and fault tolerance library designed to isolate points of access to remote systems,
services and 3rd party libraries, stop cascading failure and enable resilience in complex distributed systems where failure is inevitable.


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
