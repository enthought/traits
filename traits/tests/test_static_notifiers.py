# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for the static notifiers. """
import unittest

from traits import trait_notifiers
from traits.api import Float, HasTraits, List


calls_0 = []


class StaticNotifiers0(HasTraits):
    ok = Float

    def _ok_changed():
        calls_0.append(True)

    fail = Float

    def _fail_changed():
        raise Exception("error")


class StaticNotifiers1(HasTraits):
    ok = Float

    def _ok_changed(self):
        if not hasattr(self, "calls"):
            self.calls = []
        self.calls.append(True)

    fail = Float

    def _fail_changed(self):
        raise Exception("error")


class StaticNotifiers2(HasTraits):
    ok = Float

    def _ok_changed(self, new):
        if not hasattr(self, "calls"):
            self.calls = []
        self.calls.append(new)

    fail = Float

    def _fail_changed(self, new):
        raise Exception("error")


class StaticNotifiers3(HasTraits):
    ok = Float

    def _ok_changed(self, old, new):
        if not hasattr(self, "calls"):
            self.calls = []
        self.calls.append((old, new))

    fail = Float

    def _fail_changed(self, old, new):
        raise Exception("error")


class StaticNotifiers4(HasTraits):
    ok = Float

    def _ok_changed(self, name, old, new):
        if not hasattr(self, "calls"):
            self.calls = []
        self.calls.append((name, old, new))

    fail = Float

    def _fail_changed(self, name, old, new):
        raise Exception("error")


class _LeadingUnderscore(HasTraits):
    _ok = Float()
    calls = List()

    def __ok_changed(self, name, old, new):
        self.calls.append((name, old, new))


class TestNotifiers(unittest.TestCase):
    """ Tests for the static notifiers, and the "anytrait" static notifiers.
    """

    def setUp(self):
        self.exceptions = []
        trait_notifiers.push_exception_handler(self._handle_exception)

    def tearDown(self):
        trait_notifiers.pop_exception_handler()

    def _handle_exception(self, obj, name, old, new):
        self.exceptions.append((obj, name, old, new))

    def test_static_notifiers_0(self):
        calls_0.clear()

        obj = StaticNotifiers0(ok=2)
        obj.ok = 3
        self.assertEqual(len(calls_0), 2)

        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_static_notifiers_1(self):
        obj = StaticNotifiers1(ok=2)
        obj.ok = 3
        self.assertEqual(len(obj.calls), 2)

        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_static_notifiers_2(self):
        obj = StaticNotifiers2(ok=2)
        obj.ok = 3
        self.assertEqual(obj.calls, [2, 3])
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_static_notifiers_3(self):
        obj = StaticNotifiers3(ok=2)
        obj.ok = 3
        self.assertEqual(obj.calls, [(0, 2), (2, 3)])
        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_static_notifiers_4(self):
        obj = StaticNotifiers4(ok=2)
        obj.ok = 3
        self.assertEqual(obj.calls, [("ok", 0, 2), ("ok", 2, 3)])

        obj.fail = 1
        self.assertEqual(self.exceptions, [(obj, "fail", 0, 1)])

    def test_leading_underscore(self):
        """ Test the name-mangling for the double-underscored change handlers.
        """
        obj = _LeadingUnderscore(_ok=2.0)
        obj._ok = 3.0
        self.assertEqual(obj.calls, [("_ok", 0.0, 2.0), ("_ok", 2.0, 3.0)])
