# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Unit tests to ensure that we can call reset_traits/delete on a
property trait (regression tests for Github issue #67).

"""

import unittest

from traits.api import Any, HasTraits, Int, Property, TraitError


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
        self.assertCountEqual(unresetable, ["a", "b"])
