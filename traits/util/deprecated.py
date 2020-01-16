""" A decorator for marking methods/functions as deprecated. """

# Standard library imports.
import functools
import warnings


def deprecated(message):
    """ A factory for decorators for marking methods/functions as deprecated.

    """

    def decorator(fn):
        """ A decorator for marking methods/functions as deprecated. """

        @functools.wraps(fn)
        def wrapper(*args, **kw):
            """ The method/function wrapper. """

            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return fn(*args, **kw)

        return wrapper

    return decorator
