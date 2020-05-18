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

from traits.api import Expression, HasTraits, Int, TraitError


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

    def test_default_method(self):
        class Foo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

            default_calls = Int(0)

            def _bar_default(self):
                self.default_calls += 1
                return "1"

        f = Foo()
        self.assertEqual(f.bar, "1")
        self.assertEqual(f.bar_, compile("1", "<string>", "eval"))
        self.assertEqual(f.default_calls, 1)

        # Check that the order doesn't matter
        f2 = Foo()
        self.assertEqual(f2.bar_, compile("1", "<string>", "eval"))
        self.assertEqual(f2.bar, "1")
        self.assertEqual(f2.default_calls, 1)

    def test_default_method_non_valid(self):
        class Foo(HasTraits):
            bar = Expression()

            def _bar_default(self):
                return "{x=y"

        f = Foo()
        msg = "The 'bar' trait of a Foo instance must be a valid"
        with self.assertRaisesRegex(TraitError, msg):
            f.bar

    @unittest.expectedFailure  # FIXME issue #1096
    def test_default_static_override_static(self):
        class BaseFoo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

        class Foo(BaseFoo):
            bar = "3"

        f = Foo()
        self.assertEqual(f.bar, "3")
        self.assertEqual(f.bar_, compile("3", "<string>", "eval"))

    def test_default_static_override_method(self):
        class BaseFoo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

        class Foo(BaseFoo):
            default_calls = Int(0)

            def _bar_default(self):
                self.default_calls += 1
                return "3"

        f = Foo()
        self.assertEqual(f.bar, "3")
        self.assertEqual(f.bar_, compile("3", "<string>", "eval"))
        self.assertEqual(f.default_calls, 1)

    @unittest.expectedFailure   # FIXME issue #1096
    def test_default_method_override_static(self):
        class BaseFoo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

            default_calls = Int(0)

            def _bar_default(self):
                self.default_calls += 1
                return "1"

        class Foo(BaseFoo):
            bar = "3"

        f = Foo()
        self.assertEqual(f.bar, "3")
        self.assertEqual(f.bar_, compile("3", "<string>", "eval"))
        self.assertEqual(f.default_calls, 0)

    def test_default_method_override_method(self):
        class BaseFoo(HasTraits):
            # The default value set in the class definition is "0"
            bar = Expression()

            default_calls = Int(0)

            def _bar_default(self):
                self.default_calls += 1
                return "1"

        class Foo(BaseFoo):
            def _bar_default(self):
                self.default_calls += 1
                return "3"

        f = Foo()
        self.assertEqual(f.bar, "3")
        self.assertEqual(f.bar_, compile("3", "<string>", "eval"))
        self.assertEqual(f.default_calls, 1)
