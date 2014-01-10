#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, Int, Range, Str


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


class RangeTestCase(unittest.TestCase):

    def test_non_ui_events(self):

        obj = WithFloatRange()
        obj._changed_handler_calls = 0

        obj.r = 10
        self.failUnlessEqual(1, obj._changed_handler_calls)

        obj._changed_handler_calls = 0
        obj.r = 34.56
        self.failUnlessEqual(2, obj._changed_handler_calls)
        self.failUnlessEqual(40, obj.r)

    def test_non_ui_int_events(self):

        # Even thou the range is configured for 0..1000, the handler resets
        # the value to 0 when it exceeds 100.
        obj = WithLargeIntRange()
        obj._changed_handler_calls = 0

        obj.r = 10
        self.failUnlessEqual(1, obj._changed_handler_calls)
        self.failUnlessEqual(10, obj.r)

        obj.r = 100
        self.failUnlessEqual(2, obj._changed_handler_calls)
        self.failUnlessEqual(100, obj.r)

        obj.r = 101
        self.failUnlessEqual(4, obj._changed_handler_calls)
        self.failUnlessEqual(0, obj.r)
