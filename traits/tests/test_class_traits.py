"""
Unit tests for the `HasTraits.class_traits` class function.

"""

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, Int, List, Str


class A(HasTraits):

    x = Int

    name = Str(marked=True)


class B(A):

    pass


class C(B):

    lst = List(marked=False)

    y = Int(marked=True)


class TestClassTraits(unittest.TestCase):

    def test_all_class_traits(self):
        expected = ['x', 'name', 'trait_added', 'trait_modified']
        self.assertItemsEqual(expected, A.class_traits())

        # Check that derived classes report the correct traits.
        self.assertItemsEqual(expected, B.class_traits())

        expected.extend(('lst', 'y'))
        self.assertItemsEqual(expected, C.class_traits())

    def test_class_traits_with_metadata(self):

        # Retrieve all traits that have the `marked` metadata
        # attribute set to True.
        traits = C.class_traits(marked=True)
        self.assertItemsEqual(('y', 'name'), traits.keys())

        # Retrieve all traits that have a `marked` metadata attribute,
        # regardless of its value.
        marked_traits = C.class_traits(marked=lambda attr: attr is not None)
        self.assertItemsEqual(('y', 'name', 'lst'), marked_traits)
