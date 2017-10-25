# coding=utf8



import abc
import gevent
import logging
import signal
import traceback
from functools import wraps
from contextlib import contextmanager

_logger = logging.getLogger(__name__)



"""
log format: 

log_level=DEBUG log_time=2017-10-24 10:01:58.728277 command_name=HelloWorldCommand timeout=2000 result=ok execute=200
log_level=DEBUG log_time=2017-10-24 10:01:58.728277 command_name=HelloWorldCommand timeout=2000 result=fail execute=200 fallback=310 cache=92
log_level=DEBUG log_time=2017-10-24 10:01:58.728277 command_name=HelloWorldCommand timeout=2000 result=fail execute=200 fallback=310 cache=92
log_level=DEBUG log_time=2017-10-24 10:01:58.728277 command_name=HelloWorldCommand timeout=2000 result=fail execute=200 fallback=310 cache=92
"""

class TubbeTimeoutException(Exception):
    pass

def _fallback(fallback_func):
    def deco(f):
        @wraps(f)
        def _(*a, **kw):
            try:
                return f(*a, **kw)
            except:
                # already printed to stderr \
                #        in greenlet's join function.
                return fallback_func(*a, **kw)
        return _
    return deco


@contextmanager
def timeout(seconds):
    def _handle_timeout(signum, frame):
        raise TubbeTimeoutException('timeout')

    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.alarm(seconds)
    yield

class AbstractCommand(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, timeout=None, logger=None):
        self.name = name
        self.timeout = timeout
        self.logger = logger or _logger

    @abc.abstractmethod
    def run(self, *a, **kw):
        pass

    @abc.abstractmethod
    def fallback(self, *a, **kw):
        pass

    @abc.abstractmethod
    def cache(self, *a, **kw):
        pass

class BaseCommand(AbstractCommand):

    def run(self, *a, **kw):
        raise NotImplemented

    def fallback(self, *a, **kw):
        raise NotImplemented

    def cache(self, *a, **kw):
        raise NotImplemented


class NoCacheCommand(AbstractCommand):

    def run(self, *a, **kw):
        raise NotImplemented

    def fallback(self, *a, **kw):
        raise NotImplemented

    def cache(self, *a, **kw):
        return


class BaseGeventCommand(BaseCommand):

    def _do_cache(self, *a, **kw):
        # TODO: logging
        return self.cache(*a, **kw)

    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        # TODO: logging
        job = gevent.Greenlet.spawn(self.fallback, *a, **kw)
        job.join(self.timeout)
        return job.get(block=False, timeout=self.timeout)

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        # TODO: logging
        job = gevent.Greenlet.spawn(self.run, *a, **kw)
        job.join(self.timeout)
        return job.get(block=False, timeout=self.timeout)


class BaseSyncCommand(BaseCommand):

    def _do_cache(self, *a, **kw):
        # TODO: logging
        return self.cache(*a, **kw)

    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        # TODO: logging
        with timeout(self.timeout):
            return self.fallback(*a, **kw)

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        # TODO: logging
        with timeout(self.timeout):
            return self.run(*a, **kw)



if __name__ == "__main__":
    import time
    from gevent import monkey
    monkey.patch_all()

    class PowCommand(BaseGeventCommand):
    #class PowCommand(BaseSyncCommand):

        def run(self, n):
            raise Exception('a')
            return pow(n, 2)

        def fallback(self, n):
            time.sleep(3)
            return pow(n, 3)

        def cache(self, n):
            return pow(n, 4)

    c = PowCommand('pow', 2)
    print c.execute(3)
