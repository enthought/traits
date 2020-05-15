# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import Expression, HasTraits


class TestExpression(unittest.TestCase):

    def test_set_value_original(self):
        class Foo(HasTraits):
            bar = Expression()

        f = Foo()
        f.bar = "1"
        self.assertEqual(f.bar, "1")

    def test_default_value_original(self):
        class Foo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression(default_value="1")

        f = Foo()
        self.assertEqual(f.bar, "1")

    def test_default_method_original(self):
        class Foo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

            def _bar_default(self):
                return "1"

        f = Foo()
        self.assertEqual(f.bar, "1")

    def test_default_method_non_valid(self):
        class Foo(HasTraits):
            bar = Expression()

            def _bar_default(self):
                return "{x=y"

        f = Foo()
        # Raised exception is layered, therefore check only for base Exception
        with self.assertRaises(Exception):
            getattr(f, "bar")
