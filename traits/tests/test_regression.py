""" General regression tests for a variety of bugs. """
import gc
import sys

from traits.has_traits import HasTraits, Property
from traits.trait_types import Int
from traits.testing.unittest_tools import unittest

class Dummy(HasTraits):
    x = Int(10)



def _create_subclass():
    class Subclass(HasTraits):
        pass
    return Subclass


class TestRegression(unittest.TestCase):

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

    def test_subclasses_weakref(self):
        """ Make sure that dynamically created subclasses are not held
        strongly by HasTraits.
        """
        previous_subclasses = HasTraits.__subclasses__()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        gc.collect()
        self.assertEqual(previous_subclasses, HasTraits.__subclasses__())

    def test_leaked_property_tuple(self):
        """ the property ctrait constructor shouldn't leak a tuple. """
        class A(HasTraits):
            prop = Property()
        a = A()
        self.assertEqual(sys.getrefcount(a.trait('prop').property()), 1)


if __name__ == '__main__':
    unittest.main()
