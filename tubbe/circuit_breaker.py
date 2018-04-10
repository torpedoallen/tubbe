# coding=utf8



import abc
import traceback

from switch_client.base import get_switch_info_plus, LocalPrioritizedClient


class AbstractCircuitBreaker(object):

    __metaclass__ = abc.ABCMeta


    def __init__(self, name):
        self.name = name

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

    def break_or_not(self, counter):
        try:
            # NOTE: default not break
            val = get_switch_info_plus(self.name, {u'toggle': False},
                                    client_class=LocalPrioritizedClient,
                                    expire_interval=5)
            return val[u'toggle'] == True
        except:
            traceback.print_exc()
            return False
