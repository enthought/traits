import unittest
import warnings

from traits.util.deprecated import clear_deprecation_cache

from .deprecated_things import Bar, Foo, func


# TODO: test logging


class TestDeprecated(unittest.TestCase):

    def setUp(self):
        clear_deprecation_cache()

    def test_deprecated_function(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            func(1, 2)

        self.assertEqual(func.__name__, 'func')
        self.assertEqual(func.__doc__, 'Function docstring.')

        self.assertEqual(len(w), 1)
        self.assertEqual('deprecated function', str(w[0].message))

    def test_deprecated_method(self):
        foo = Foo()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            foo.meth(0)

        self.assertEqual(foo.meth.__name__, 'meth')
        self.assertEqual(foo.meth.__doc__, 'Method docstring.')

        self.assertEqual(len(w), 1)
        self.assertEqual('deprecated method', str(w[0].message))

    def test_deprecated_constructor(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            Bar()

        self.assertEqual(Bar.__init__.__name__, '__init__')
        self.assertEqual(Bar.__init__.__doc__, 'Constructor docstring.')

        self.assertEqual(len(w), 1)
        self.assertEqual('deprecated class', str(w[0].message))

    def test_clear_cache(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            func(1, 2)
        self.assertEqual(len(w), 1)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            func(1, 2)
        self.assertEqual(len(w), 0)

        clear_deprecation_cache()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            func(1, 2)
        self.assertEqual(len(w), 1)
