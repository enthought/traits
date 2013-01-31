""" General regression tests for a variety of bugs.
"""

from unittest import TestCase

from traits.api import HasTraits, Int


class Dummy(HasTraits):
    x = Int(10)


class TestRegression(TestCase):
    def test_default_value_for_no_cache(self):
        """ Make sure that CTrait.default_value_for() does not cache the
        result.
        """
        dummy = Dummy()
        # Nothing in the __dict__ yet.
        self.assertEqual(dummy.__dict__, {})
        ctrait = dummy.trait('x')
        default = ctrait.default_value_for(dummy, 'x')
        self.assertEqual(default, 10)
        self.assertEqual(dummy.__dict__, {})
