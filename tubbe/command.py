# coding=utf8



import abc
import gevent
import logging
import signal
import datetime
import traceback
from functools import wraps
from contextlib import contextmanager

_logger = logging.getLogger(__name__)



class TubbeTimeoutException(Exception):
    pass

def _fallback(callback):
    def deco(f):
        @wraps(f)
        def _(*a, **kw):
            try:
                return f(*a, **kw)
            except:
                return callback(*a, **kw)
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


class BaseAsyncCommand(BaseCommand):

    def _do_cache(self, *a, **kw):
        start_time = datetime.datetime.now()
        v = self.cache(*a, **kw)
        self.logger.info({
            'command': self.name,
            'action': 'cache',
            'fallback': None,
            'timeout': self.timeout,
            'success': 'yes',
            'start_time': start_time,
            'end_time': datetime.datetime.now(),
            })
        return v



    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        start_time = datetime.datetime.now()
        job = gevent.Greenlet.spawn(self.fallback, *a, **kw)
        job.join(self.timeout)
        try:
            v = job.get(block=False, timeout=self.timeout)
            self.logger.info({
                'command': self.name,
                'action': 'fallback',
                'fallback': None,
                'timeout': self.timeout,
                'success': 'yes',
                'start_time': start_time,
                'end_time': datetime.datetime.now(),
                })

            return v
        except:
            self.logger.error({
                'command': self.name,
                'action': 'fallback',
                'fallback': str(self.cache),
                'timeout': self.timeout,
                'success': 'no',
                'start_time': start_time,
                'end_time': datetime.datetime.now(),
                })

            raise

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        # TODO: logging
        start_time = datetime.datetime.now()
        job = gevent.Greenlet.spawn(self.run, *a, **kw)
        job.join(self.timeout)
        try:
            v = job.get(block=False, timeout=self.timeout)
            self.logger.info({
                'command': self.name,
                'action': 'execute',
                'fallback': None,
                'timeout': self.timeout,
                'success': 'yes',
                'start_time': start_time,
                'end_time': datetime.datetime.now(),
                })

            return v
        except:
            self.logger.error({
                'command': self.name,
                'action': 'execute',
                'fallback': str(self.fallback),
                'timeout': self.timeout,
                'success': 'no',
                'start_time': start_time,
                'end_time': datetime.datetime.now(),
                })
            raise




class BaseSyncCommand(BaseCommand):

    def _do_cache(self, *a, **kw):
        start_time = datetime.datetime.now()
        v = self.cache(*a, **kw)
        self.logger.info({
            'command': self.name,
            'action': 'cache',
            'fallback': None,
            'timeout': self.timeout,
            'success': 'yes',
            'start_time': start_time,
            'end_time': datetime.datetime.now(),
            })

        return v

    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        with timeout(self.timeout):
            start_time = datetime.datetime.now()
            try:
                v = self.fallback(*a, **kw)
                self.logger.info({
                    'command': self.name,
                    'action': 'fallback',
                    'fallback': None,
                    'timeout': self.timeout,
                    'success': 'yes',
                    'start_time': start_time,
                    'end_time': datetime.datetime.now(),
                    })
                return v
            except:
                self.logger.error({
                    'command': self.name,
                    'action': 'fallback',
                    'fallback': str(self.cache),
                    'timeout': self.timeout,
                    'success': 'no',
                    'start_time': start_time,
                    'end_time': datetime.datetime.now(),
                    })
                raise

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        # TODO: logging
        with timeout(self.timeout):
            start_time = datetime.datetime.now()
            try:
                v = self.run(*a, **kw)
                self.logger.info({
                    'command': self.name,
                    'action': 'execute',
                    'fallback': None,
                    'timeout': self.timeout,
                    'success': 'yes',
                    'start_time': start_time,
                    'end_time': datetime.datetime.now(),
                    })
                return v
            except:
                self.logger.error({
                    'command': self.name,
                    'action': 'execute',
                    'fallback': str(self.fallback),
                    'timeout': self.timeout,
                    'success': 'no',
                    'start_time': start_time,
                    'end_time': datetime.datetime.now(),
                    })
                raise

