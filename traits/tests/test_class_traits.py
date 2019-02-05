"""
Unit tests for the `HasTraits.class_traits` class function.

"""

from __future__ import absolute_import

import unittest

import six

from traits.api import HasTraits, Int, List, Str


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
        expected = ["x", "name", "trait_added", "trait_modified"]
        six.assertCountEqual(self, A.class_traits(), expected)

        # Check that derived classes report the correct traits.
        six.assertCountEqual(self, B.class_traits(), expected)

        expected.extend(("lst", "y"))
        six.assertCountEqual(self, C.class_traits(), expected)

    def test_class_traits_with_metadata(self):

        # Retrieve all traits that have the `marked` metadata
        # attribute set to True.
        traits = C.class_traits(marked=True)
        six.assertCountEqual(self, list(traits.keys()), ("y", "name"))

        # Retrieve all traits that have a `marked` metadata attribute,
        # regardless of its value.
        marked_traits = C.class_traits(marked=lambda attr: attr is not None)
        six.assertCountEqual(self, marked_traits, ("y", "name", "lst"))
