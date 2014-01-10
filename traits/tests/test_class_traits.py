"""
Unit tests for the `HasTraits.class_traits` class function.

"""

from __future__ import absolute_import

from traits import _py2to3

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
        _py2to3.assertCountEqual(self, A.class_traits(), expected)

        # Check that derived classes report the correct traits.
        _py2to3.assertCountEqual(self, B.class_traits(), expected)

        expected.extend(('lst', 'y'))
        _py2to3.assertCountEqual(self, C.class_traits(), expected)

    def test_class_traits_with_metadata(self):

        # Retrieve all traits that have the `marked` metadata
        # attribute set to True.
        traits = C.class_traits(marked=True)
        _py2to3.assertCountEqual(self, traits.keys(), ('y', 'name'))

        # Retrieve all traits that have a `marked` metadata attribute,
        # regardless of its value.
        marked_traits = C.class_traits(marked=lambda attr: attr is not None)
        _py2to3.assertCountEqual(self, marked_traits, ('y', 'name', 'lst'))
