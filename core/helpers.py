from django.db.models import Func


def anyway(func, exceptions, default_value=None):
    ''' return default_value in case of one of exceptions'''
    try:
        return func()
    except exceptions:
        return default_value


def auto_str(cls):
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % item for item in vars(self).items() if item[0] != '_state')
        )

    cls.__str__ = __str__
    return cls


def checked_value(value, _min, _max, value_when_out_of_range=None):
    if value < _min:
        if abs(value - _min) < 0.001:
            return _min
    elif value > _max:
        if abs(value - _max) < 0.001:
            return _max
    else:
        return value
    return value_when_out_of_range



class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'

