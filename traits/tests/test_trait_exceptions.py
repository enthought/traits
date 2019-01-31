# ------------------------------------------------------------------------------
# Copyright (c) 2015, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# ------------------------------------------------------------------------------

import unittest

from traits.api import HasTraits, Int


class A(HasTraits):
    x = Int(5)


class TestGetAttr(unittest.TestCase):
    def setUp(self):
        self.a = A()

    def test_bad__getattribute__(self):
        # Argument to __getattribute__ must be a string
        self.assertEqual(self.a.__getattribute__("x"), 5)

        with self.assertRaises(TypeError) as e:
            self.a.__getattribute__(2)

        # Error message contains value and type of bad attribute name
        exception_msg = str(e.exception)
        self.assertIn("2", exception_msg)
        self.assertIn("int", exception_msg)
