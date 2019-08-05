# coding=utf8

from __future__ import absolute_import

import six
import abc
import gevent
import logging
import signal
import datetime
import traceback
import socket

from functools import wraps
from collections import OrderedDict
from six import with_metaclass


from . import exceptions
from .circuit_breaker import PositiveCircuitBreaker
from .metrics import Counter

_logger = logging.getLogger(__name__)

__all__ = ['BaseGeventCommand', 'BaseSyncCommand']


def datetime_formatter(dt):
    if not dt:
        return ''

    if not isinstance(dt, datetime.datetime):
        return ''

    return dt.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

def _fallback(callback):
    def deco(f):
        @wraps(f)
        def _(*a, **kw):
            command = a[0]
            name = command.name
            timeout = command.timeout
            start_time = datetime.datetime.now()
            action = f.__name__
            fallback = callback and callback.__name__ or None
            try:
                v = f(*a, **kw)
                # Counter: normal + 1
                command.counter.incr_normal()

                # logging
                end_time = datetime.datetime.now()
                _info = OrderedDict([
                    ('log_time', datetime_formatter(start_time)),
                    ('hostname', socket.gethostname()),
                    ('command', name),
                    ('args', a),
                    ('kwargs', kw),
                    ('action', action),
                    ('fallback', fallback),
                    ('timeout', timeout),
                    ('success', True),
                    ('reason', ''),
                    ('end_time', datetime_formatter(end_time)),
                    ('duration_ms', (end_time - start_time).total_seconds()*1000),
                    ('error_ratio', command.counter.error_ratio),
                    ('error_number', command.counter.current_window.error_number),
                    ('total_number', command.counter.current_window.total_number),
                    ('window_created_time', datetime_formatter(command.counter.current_window.created_time)),
                    ('supposed_to_break', not command.counter.is_available()),
                    ])
                command.logger.info('\t'.join(['%s=%s' % t for t in _info.items()]))
                return v
            except BaseException as e:
                # Counter: error + 1
                command.counter.incr_error()

                end_time = datetime.datetime.now()
                _info = OrderedDict([
                    ('log_time', datetime_formatter(start_time)),
                    ('hostname', socket.gethostname()),
                    ('command', name),
                    ('args', a),
                    ('kwargs', kw),
                    ('action', action),
                    ('fallback', fallback),
                    ('timeout', timeout),
                    ('success', False),
                    ('reason', hasattr(e, 'reason') and e.reason or e.message),
                    ('end_time', datetime_formatter(end_time)),
                    ('duration_ms', (end_time - start_time).total_seconds()*1000),
                    ('error_ratio', command.counter.error_ratio),
                    ('error_number', command.counter.current_window.error_number),
                    ('total_number', command.counter.current_window.total_number),
                    ('window_created_time', datetime_formatter(command.counter.current_window.created_time)),
                    ('supposed_to_break', not command.counter.is_available()),
                    ])
                command.logger.error('\t'.join(['%s=%s' % t for t in _info.items()]))

                # NOTE: raise in cache method
                if not callback:
                    raise

                return callback(*a, **kw)
        return _
    return deco


class _timeout(object):


    def __init__(self, seconds):
        self.timeout = seconds
        super(_timeout, self).__init__()

    def _start(self):
        self.sig_handler = signal.signal(signal.SIGALRM, self.__handler)
        signal.alarm(self.timeout)

    def _cleanup(self):
        # reset
        signal.signal(signal.SIGALRM, self.sig_handler)
        signal.alarm(0)

    def __enter__(self):
        self._start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()

    def __call__(self, f):
        def wrapped(*a, **kw):
            self._start()
            try:
                return f(*a, **kw)
            except exceptions.TubbeTimeoutException:
                raise
            finally:
                self._cleanup()

        return wrapped

    def __handler(self, signum, frame):
        raise exceptions.TubbeTimeoutException


def _get_fullname(f):
    return f.__module__ + "." + f.__name__

class AbstractCommand(with_metaclass(abc.ABCMeta, object)):

    def __init__(self, name,
            timeout=None, logger=None, circuit_breaker_class=None, counter=None):
        self.name = name
        self.timeout = timeout
        self.logger = logger or _logger
        self.circuit_breaker = (circuit_breaker_class or PositiveCircuitBreaker)(name)
        self.counter = counter or Counter(interval=10)

    @abc.abstractmethod
    def run(self, *a, **kw):
        pass

    @abc.abstractmethod
    def fallback(self, *a, **kw):
        pass

    @abc.abstractmethod
    def cache(self, *a, **kw):
        pass

    @abc.abstractmethod
    def validate(self, result):
        pass


class BaseCommand(AbstractCommand):

    def run(self, *a, **kw):
        raise NotImplemented

    def fallback(self, *a, **kw):
        raise NotImplemented

    def cache(self, *a, **kw):
        raise NotImplemented

    def validate(self, result):
        raise NotImplemented


class BaseGeventCommand(BaseCommand):

    @_fallback(None)
    def _do_cache(self, *a, **kw):
        return self.cache(*a, **kw)

    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        job = gevent.spawn(self.fallback, *a, **kw)
        job.join(self.timeout)
        v = job.get(block=False, timeout=self.timeout)
        if not self.validate(v):
            raise exceptions.TubbeValidationException
        return v

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        if self.circuit_breaker.break_or_not(self.counter):
            raise exceptions.TubbeCircuitBrokenException
        job = gevent.spawn(self.run, *a, **kw)
        job.join(self.timeout)
        v = job.get(block=False, timeout=self.timeout)
        if not self.validate(v):
            raise exceptions.TubbeValidationException
        return v


class BaseSyncCommand(BaseCommand):

    @_fallback(None)
    def _do_cache(self, *a, **kw):
        return self.cache(*a, **kw)

    @_fallback(_do_cache)
    def _do_fallback(self, *a, **kw):
        with _timeout(self.timeout):
            v = self.fallback(*a, **kw)
            if not self.validate(v):
                raise exceptions.TubbeValidationException
            return v

    @_fallback(_do_fallback)
    def execute(self, *a, **kw):
        with _timeout(self.timeout):
            if self.circuit_breaker.break_or_not(self.counter):
                raise exceptions.TubbeCircuitBrokenException

            v = self.run(*a, **kw)
            if not self.validate(v):
                raise exceptions.TubbeValidationException
            return v

