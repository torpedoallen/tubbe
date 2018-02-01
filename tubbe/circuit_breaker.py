# coding=utf8



import abc


class AbstractCircuitBreaker(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def break_or_not(self, *a, **kw):
        pass


class PositiveCircuitBreaker(AbstractCircuitBreaker):
    ''' alway pass'''

    def break_or_not(self, counter):
        return False


class NegativeCircuitBreaker(AbstractCircuitBreaker):
    ''' alway fail'''

    def break_or_not(self, counter):
        return True


class DefaultCircuitBreaker(AbstractCircuitBreaker):
    ''' with built-in counter '''

    def break_or_not(self, counter):
        return not counter.is_available()
