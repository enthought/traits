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

from traits.testing.api import UnittestTools
from traits.util.api import deprecated


@deprecated("Addition is deprecated; use subtraction instead.")
def my_deprecated_addition(x, y):
    return x + y


@deprecated("Broken code. Use something else.")
def my_bad_function():
    1 / 0


class ClassWithDeprecatedBits(object):
    @deprecated("bits are deprecated; use bytes")
    def bits(self):
        return 42

    @deprecated("bytes are deprecated too. Use base 10.")
    def bytes(self, required_arg, *args, **kwargs):
        return required_arg, args, kwargs


class TestDeprecated(unittest.TestCase, UnittestTools):
    def test_deprecated_function(self):
        with self.assertDeprecated():
            result = my_deprecated_addition(42, 1729)
        self.assertEqual(result, 1771)

    def test_deprecated_exception_raising_function(self):
        with self.assertRaises(ZeroDivisionError):
            with self.assertDeprecated():
                my_bad_function()

    def test_deprecated_method(self):
        obj = ClassWithDeprecatedBits()
        with self.assertDeprecated():
            result = obj.bits()
        self.assertEqual(result, 42)

    def test_deprecated_method_with_fancy_signature(self):
        obj = ClassWithDeprecatedBits()
        with self.assertDeprecated():
            result = obj.bytes(3, 27, 65, name="Boris", age=-3.2)
        self.assertEqual(result, (3, (27, 65), {"name": "Boris", "age": -3.2}))
