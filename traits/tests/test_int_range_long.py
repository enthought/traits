#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

import unittest

import six

from traits.api import HasTraits, Int, Range, Long, TraitError

int = int


class A(HasTraits):
    i = Int
    l = Long
    r = Range(int(2), int(9223372036854775807))


class TraitIntRangeLong(unittest.TestCase):
    def test_int(self):
        "Test to make sure it is legal to set an Int trait to a long value"
        a = A()
        a.i = 1
        a.i = int(10)

    def test_long(self):
        "Test if it is legal to set a Long trait to an int value"
        a = A()
        a.l = 10
        a.l = int(100)

    def test_range(self):
        "Test a range trait with longs being set to an int value"
        a = A()
        a.r = 256
        a.r = int(20)
        self.assertRaises(TraitError, a.trait_set, r=int(1))
        self.assertRaises(
            TraitError, a.trait_set, r=int(9223372036854775808)
        )
