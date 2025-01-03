# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.trait_types import Int
from traits.has_traits import HasTraits


class Foo(HasTraits):

    bar = Int

    def _bar_default(self):
        return 4


class TestTraitDefaultInitializer(unittest.TestCase):
    """ Test basic usage of the default method.

    """

    def test_default_value(self):
        foo = Foo()
        self.assertEqual(foo.bar, 4)

    def test_default_value_override(self):
        foo = Foo(bar=3)
        self.assertEqual(foo.bar, 3)

    def test_reset_to_default(self):
        foo = Foo(bar=3)
        foo.reset_traits(traits=["bar"])
        self.assertEqual(foo.bar, 4)

    def test_error_propagation_in_default_methods(self):
        class FooException(Foo):
            def _bar_default(self):
                1 / 0

        foo = FooException()
        self.assertRaises(ZeroDivisionError, lambda: foo.bar)

        class FooKeyError(Foo):
            def _bar_default(self):
                raise KeyError()

        # Check that KeyError is propagated (issue #70).
        foo = FooKeyError()
        self.assertRaises(KeyError, lambda: foo.bar)
