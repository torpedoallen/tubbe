# coding=utf8



import abc


class AbstractCircuitBreaker(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def break_or_not(self, *a, **kw):
        pass


class DummyCircuitBreaker(AbstractCircuitBreaker):
    ''' alway pass'''

    def break_or_not(self, counter):
        return False


class DefaultCircuitBreaker(AbstractCircuitBreaker):
    ''' with built-in counter '''

    def break_or_not(self, counter):
        return not counter.is_available()
