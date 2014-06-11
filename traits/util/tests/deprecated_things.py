""" Test items used by test_deprecated.py . """

from traits.util.deprecated import deprecated


@deprecated('deprecated function')
def func(x, y):
    """Function docstring."""


class Foo(object):
    @deprecated('deprecated method')
    def meth(self, a):
        """Method docstring."""


class Bar(object):
    @deprecated('deprecated class')
    def __init__(self):
        """Constructor docstring."""
