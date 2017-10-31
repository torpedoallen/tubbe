# coding=utf8



class TubbeBaseException(Exception):
    reason = ''

class TubbeTimeoutException(TubbeBaseException):
    reason = 'invoking timeout'

class TubbeCircuitBrokenException(TubbeBaseException):
    reason = 'circuit breaker works'

class TubbeValidationException(TubbeBaseException):
    reason = 'validation error'
