# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Unit tests for the `HasTraits.class_traits` class function.

"""

import unittest

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
        self.assertCountEqual(A.class_traits(), expected)

        # Check that derived classes report the correct traits.
        self.assertCountEqual(B.class_traits(), expected)

        expected.extend(("lst", "y"))
        self.assertCountEqual(C.class_traits(), expected)

    def test_class_traits_with_metadata(self):

        # Retrieve all traits that have the `marked` metadata
        # attribute set to True.
        traits = C.class_traits(marked=True)
        self.assertCountEqual(list(traits.keys()), ("y", "name"))

        # Retrieve all traits that have a `marked` metadata attribute,
        # regardless of its value.
        marked_traits = C.class_traits(marked=lambda attr: attr is not None)
        self.assertCountEqual(marked_traits, ("y", "name", "lst"))
