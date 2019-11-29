#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

import unittest

from traits.api import HasTraits, Int, Range, Str, TraitError


class WithFloatRange(HasTraits):
    r = Range(0.0, 100.0)
    r_copied_on_change = Str

    _changed_handler_calls = Int

    def _r_changed(self, old, new):
        self._changed_handler_calls += 1
        self.r_copied_on_change = str(self.r)

        if (self.r % 10) > 0:
            self.r += 10 - (self.r % 10)


class WithLargeIntRange(HasTraits):
    r = Range(0, 1000)
    r_copied_on_change = Str

    _changed_handler_calls = Int

    def _r_changed(self, old, new):
        self._changed_handler_calls += 1
        self.r_copied_on_change = str(self.r)

        if self.r > 100:
            self.r = 0


class WithDynamicRange(HasTraits):
    low = Int(0)
    high = Int(10)
    value = Int(3)

    r = Range(value="value", low="low", high="high", exclude_high=True)

    def _r_changed(self, old, new):
        self._changed_handler_calls += 1


class RangeTestCase(unittest.TestCase):
    def test_non_ui_events(self):

        obj = WithFloatRange()
        obj._changed_handler_calls = 0

        obj.r = 10
        self.assertEqual(1, obj._changed_handler_calls)

        obj._changed_handler_calls = 0
        obj.r = 34.56
        self.assertEqual(obj._changed_handler_calls, 2)
        self.assertEqual(obj.r, 40)

    def test_non_ui_int_events(self):

        # Even though the range is configured for 0..1000, the handler resets
        # the value to 0 when it exceeds 100.
        obj = WithLargeIntRange()
        obj._changed_handler_calls = 0

        obj.r = 10
        self.assertEqual(obj._changed_handler_calls, 1)
        self.assertEqual(obj.r, 10)

        obj.r = 100
        self.assertEqual(obj._changed_handler_calls, 2)
        self.assertEqual(obj.r, 100)

        obj.r = 101
        self.assertEqual(obj._changed_handler_calls, 4)
        self.assertEqual(obj.r, 0)

    def test_dynamic_events(self):

        obj = WithDynamicRange()
        obj._changed_handler_calls = 0

        obj.r = 5
        self.assertEqual(obj._changed_handler_calls, 1)
        self.assertEqual(obj.r, 5)

        with self.assertRaises(TraitError):
            obj.r = obj.high
        self.assertEqual(obj.r, 5)
