# validator.py --- Example of a validator function

def bounded_string(object, name, value):
    if not isinstance(value, basestring):
        raise TypeError
    if len(value) < 50:
        return value
    return '%s...%s' % (value[:24], value[-23:])
