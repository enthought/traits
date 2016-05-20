"""
Unit tests to ensure that we can call reset_traits/delete on a
property trait (regression tests for Github issue #67).

"""

from traits import _py2to3
from traits.api import Any, HasTraits, Int, Property, TraitError
from traits.testing.unittest_tools import unittest


class E(HasTraits):

    a = Property(Any)

    b = Property(Int)


class TestPropertyDelete(unittest.TestCase):

    def test_property_delete(self):
        e = E()
        with self.assertRaises(TraitError):
            del e.a
        with self.assertRaises(TraitError):
            del e.b

    def test_property_reset_traits(self):
        e = E()
        unresetable = e.reset_traits()
        _py2to3.assertCountEqual(self, unresetable, ['a', 'b'])
