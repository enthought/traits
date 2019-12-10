# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------

import unittest

from traits.api import CInt, CLong, HasTraits, Int, Long, TraitError


class ModelWithLong(HasTraits):
    n = Long()

    c = CLong()


class TestLong(unittest.TestCase):
    def test_long_is_int(self):
        # This frees us from any obligation to do more than perfunctory
        # testing of Long, since we already test Int thoroughly.
        self.assertIs(Long, Int)

    def test_clong_is_cint(self):
        # Likewise, no need to test CLong thoroughly when we already
        # have good tests for CInt.
        self.assertIs(CLong, CInt)

    def test_long(self):
        model = ModelWithLong()
        self.assertIdentical(model.n, 0)
        model.n = 34
        self.assertIdentical(model.n, 34)
        model.n = True
        self.assertIdentical(model.n, 1)
        with self.assertRaises(TraitError):
            model.n = 34.0
        with self.assertRaises(TraitError):
            model.n = "42"

    def test_clong(self):
        model = ModelWithLong()
        self.assertIdentical(model.c, 0)
        model.c = 34
        self.assertIdentical(model.c, 34)
        model.c = 37.0
        self.assertIdentical(model.c, 37)
        model.c = "42"
        self.assertIdentical(model.c, 42)

    def assertIdentical(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        self.assertEqual(actual, expected)
