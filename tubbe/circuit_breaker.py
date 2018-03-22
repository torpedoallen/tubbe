# coding=utf8



import abc

from switch_client.base import get_switch_info


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


class SwitchCircuitBreaker(AbstractCircuitBreaker):
    ''' switch service based circuit breaker '''

    def break_or_not(self, switch_name):
        val = get_switch_info(switch_name, {u'on': 100, u'off': 0})
        try:
            return val[u'off'] == 100
        except:
            return False
