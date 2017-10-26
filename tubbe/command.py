# coding=utf8



import abc
import gevent
import logging
import signal
import datetime
import traceback
from functools import wraps
from collections import OrderedDict
from contextlib import contextmanager

_logger = logging.getLogger(__name__)

__all__ = ['TubbeTimeoutException', 'timeout', 'BaseAsyncCommand', 'BaseSyncCommand']

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


def _get_fullname(f):
    return f.__module__ + "." + f.__name__

class AbstractCommand(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, timeout=None, logger=None, validator=lambda x:x):
        self.name = name
        self.timeout = timeout
        self.logger = logger or _logger
        self.validator = validator

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
        v = self.validator(v)
        _info = OrderedDict([
            ('start_time', start_time),
            ('command', self.name),
            ('action', 'cache'),
            ('fallback', None),
            ('timeout', self.timeout),
            ('success', 'yes'),
            ('end_time', datetime.datetime.now()),
            ])

        self.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
        return v



    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        start_time = datetime.datetime.now()
        job = gevent.Greenlet.spawn(self.fallback, *a, **kw)
        job.join(self.timeout)
        try:
            v = job.get(block=False, timeout=self.timeout)
            v = self.validator(v)
            _info = OrderedDict([
                ('start_time', start_time),
                ('command', self.name),
                ('action', 'fallback'),
                ('fallback', None),
                ('timeout', self.timeout),
                ('success', 'yes'),
                ('end_time', datetime.datetime.now()),
                ])
            self.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
            return v
        except:
            _info = OrderedDict([
                ('start_time', start_time),
                ('command', self.name),
                ('action', 'fallback'),
                ('fallback', _get_fullname(self.cache)),
                ('timeout', self.timeout),
                ('success', 'no'),
                ('end_time', datetime.datetime.now()),
                ])
            self.logger.error('\t'.join(['%s=%s' % t for t in _info.items()]))

            raise

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        start_time = datetime.datetime.now()
        job = gevent.Greenlet.spawn(self.run, *a, **kw)
        job.join(self.timeout)
        try:
            v = job.get(block=False, timeout=self.timeout)
            v = self.validator(v)
            _info = OrderedDict([
                ('start_time', start_time),
                ('command', self.name),
                ('action', 'execute'),
                ('fallback', None),
                ('timeout', self.timeout),
                ('success', 'yes'),
                ('end_time', datetime.datetime.now()),
                ])

            self.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
            return v
        except:
            _info = OrderedDict([
                ('start_time', start_time),
                ('command', self.name),
                ('action', 'execute'),
                ('fallback', _get_fullname(self.fallback)),
                ('timeout', self.timeout),
                ('success', 'no'),
                ('end_time', datetime.datetime.now()),
                ])
            self.logger.error('\t'.join(['%s=%s' % t for t in _info.items()]))
            raise



class BaseSyncCommand(BaseCommand):

    def _do_cache(self, *a, **kw):
        start_time = datetime.datetime.now()
        v = self.cache(*a, **kw)
        v = self.validator(v)
        _info = OrderedDict([
            ('start_time', start_time),
            ('command', self.name),
            ('action', 'cache'),
            ('fallback', None),
            ('timeout', self.timeout),
            ('success', 'yes'),
            ('end_time', datetime.datetime.now()),
            ])

        self.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
        return v

    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        with timeout(self.timeout):
            start_time = datetime.datetime.now()
            try:
                v = self.fallback(*a, **kw)
                v = self.validator(v)
                _info = OrderedDict([
                    ('start_time', start_time),
                    ('command', self.name),
                    ('action', 'fallback'),
                    ('fallback', None),
                    ('timeout', self.timeout),
                    ('success', 'yes'),
                    ('end_time', datetime.datetime.now()),
                    ])
                self.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
                return v
            except:
                _info = OrderedDict([
                    ('start_time', start_time),
                    ('command', self.name),
                    ('action', 'fallback'),
                    ('fallback', _get_fullname(self.cache)),
                    ('timeout', self.timeout),
                    ('success', 'no'),
                    ('end_time', datetime.datetime.now()),
                    ])
                self.logger.error('\t'.join(['%s=%s' % t for t in _info.items()]))
                raise

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        with timeout(self.timeout):
            start_time = datetime.datetime.now()
            try:
                v = self.run(*a, **kw)
                v = self.validator(v)
                _info = OrderedDict([
                    ('start_time', start_time),
                    ('command', self.name),
                    ('action', 'execute'),
                    ('fallback', None),
                    ('timeout', self.timeout),
                    ('success', 'yes'),
                    ('end_time', datetime.datetime.now()),
                    ])

                self.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
                return v
            except:
                _info = OrderedDict([
                    ('start_time', start_time),
                    ('command', self.name),
                    ('action', 'execute'),
                    ('fallback', _get_fullname(self.fallback)),
                    ('timeout', self.timeout),
                    ('success', 'no'),
                    ('end_time', datetime.datetime.now()),
                    ])

                self.logger.error('\t'.join(['%s=%s' % t for t in _info.items()]))
                raise

