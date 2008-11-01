import unittest
from enthought.traits.api import HasTraits, Int, Range, Long, TraitError

class A(HasTraits):
    i = Int
    l = Long
    r = Range(2L, 9223372036854775807L)


class TraitIntRangeLong(unittest.TestCase):
    def test_int(self):
        "Test to make sure it is illegal to set an Int trait to a long value"
        a = A()
        a.i = 1
        self.assertRaises(TraitError, a.set, i=10L)

    def test_long(self):
        "Test if it is legal to set a Long trait to an int value"
        a = A()
        a.l = 10
        a.l = 100L

    def test_range(self):
        "Test a range trait with longs being set to an int value"
        a = A()
        a.r = 256
        a.r = 20L
        self.assertRaises(TraitError, a.set, r=1L)
        self.assertRaises(TraitError, a.set, r=9223372036854775808L)

if __name__ == '__main__':
    unittest.main()
