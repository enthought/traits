# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Int, Range, TraitError


class A(HasTraits):
    i = Int
    r = Range(2, 9223372036854775807)


class TraitIntRange(unittest.TestCase):
    def test_int(self):
        "Test it is legal to set an Int trait to any integer value"
        a = A()
        a.i = 1
        a.i = 10**20

    def test_range(self):
        "Test a range trait with large integers being set to an int value"
        a = A()
        a.r = 256
        a.r = 20
        self.assertRaises(TraitError, a.trait_set, r=1)
        self.assertRaises(
            TraitError, a.trait_set, r=9223372036854775808
        )
