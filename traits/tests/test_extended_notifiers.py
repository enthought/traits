""" Tests for the extended notifiers.

The "extended notifiers" are set up internally when using extended traits, to
add/remove traits listeners when one of the intermediate traits changes.

For example, in a listener for the extended trait `a.b`, we need to add/remove
listeners to `a:b` when `a` changes.
"""
import unittest

import six

from traits import trait_notifiers
from traits.api import Float, HasTraits, List


class ExtendedNotifiers(HasTraits):
    def __init__(self, **traits):
        # Set up the 'extended' internal notifiers (see module docstring)

        ok_listeners = [
            self.method_listener_0,
            self.method_listener_1,
            self.method_listener_2,
            self.method_listener_3,
            self.method_listener_4,
        ]

        for listener in ok_listeners:
            self._on_trait_change(listener, "ok", dispatch="extended")

        fail_listeners = [
            self.failing_method_listener_0,
            self.failing_method_listener_1,
            self.failing_method_listener_2,
            self.failing_method_listener_3,
            self.failing_method_listener_4,
        ]

        for listener in fail_listeners:
            self._on_trait_change(listener, "fail", dispatch="extended")

        super(ExtendedNotifiers, self).__init__(**traits)

    ok = Float
    fail = Float

    # Lists where we accumulate the arguments of calls to the traits notifiers.
    rebind_calls_0 = List
    rebind_calls_1 = List
    rebind_calls_2 = List
    rebind_calls_3 = List
    rebind_calls_4 = List
    exceptions_from = List

    #### 'ok' trait listeners

    def method_listener_0(self):
        self.rebind_calls_0.append(True)

    def method_listener_1(self, new):
        self.rebind_calls_1.append(new)

    def method_listener_2(self, name, new):
        self.rebind_calls_2.append((name, new))

    def method_listener_3(self, obj, name, new):
        self.rebind_calls_3.append((obj, name, new))

    def method_listener_4(self, obj, name, old, new):
        self.rebind_calls_4.append((obj, name, old, new))

    #### 'fail' trait listeners

    def failing_method_listener_0(self):
        self.exceptions_from.append(0)
        raise Exception("error")

    def failing_method_listener_1(self, new):
        self.exceptions_from.append(1)
        raise Exception("error")

    def failing_method_listener_2(self, name, new):
        self.exceptions_from.append(2)
        raise Exception("error")

    def failing_method_listener_3(self, obj, name, new):
        self.exceptions_from.append(3)
        raise Exception("error")

    def failing_method_listener_4(self, obj, name, old, new):
        self.exceptions_from.append(4)
        raise Exception("error")


# 'ok' function listeners
calls_0 = []


def function_listener_0():
    calls_0.append(True)


calls_1 = []


def function_listener_1(new):
    calls_1.append(new)


calls_2 = []


def function_listener_2(name, new):
    calls_2.append((name, new))


calls_3 = []


def function_listener_3(obj, name, new):
    calls_3.append((obj, name, new))


calls_4 = []


def function_listener_4(obj, name, old, new):
    calls_4.append((obj, name, old, new))


# 'fail' function listeners

exceptions_from = []


def failing_function_listener_0():
    exceptions_from.append(0)
    raise Exception("error")


def failing_function_listener_1(new):
    exceptions_from.append(1)
    raise Exception("error")


def failing_function_listener_2(name, new):
    exceptions_from.append(2)
    raise Exception("error")


def failing_function_listener_3(obj, name, new):
    exceptions_from.append(3)
    raise Exception("error")


def failing_function_listener_4(obj, name, old, new):
    exceptions_from.append(4)
    raise Exception("error")


class TestExtendedNotifiers(unittest.TestCase):

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.exceptions = []
        trait_notifiers.push_exception_handler(self._handle_exception)

    def tearDown(self):
        trait_notifiers.pop_exception_handler()

    #### Private protocol #####################################################

    def _handle_exception(self, obj, name, old, new):
        self.exceptions.append((obj, name, old, new))

    #### Tests ################################################################

    def test_extended_notifiers_methods(self):
        obj = ExtendedNotifiers(ok=2)
        obj.ok = 3

        self.assertEqual(len(obj.rebind_calls_0), 2)

        expected_1 = [2, 3]
        self.assertEqual(expected_1, obj.rebind_calls_1)

        expected_2 = [("ok", 2), ("ok", 3)]
        self.assertEqual(expected_2, obj.rebind_calls_2)

        expected_3 = [(obj, "ok", 2), (obj, "ok", 3)]
        self.assertEqual(expected_3, obj.rebind_calls_3)

        expected_4 = [(obj, "ok", 0, 2), (obj, "ok", 2, 3)]
        self.assertEqual(expected_4, obj.rebind_calls_4)

    def test_extended_notifiers_methods_failing(self):
        obj = ExtendedNotifiers()
        obj.fail = 1

        six.assertCountEqual(self, [0, 1, 2, 3, 4], obj.exceptions_from)
        self.assertEqual([(obj, "fail", 0, 1)] * 5, self.exceptions)

    def test_extended_notifiers_functions(self):
        obj = ExtendedNotifiers()

        obj._on_trait_change(function_listener_0, "ok", dispatch="extended")
        obj._on_trait_change(function_listener_1, "ok", dispatch="extended")
        obj._on_trait_change(function_listener_2, "ok", dispatch="extended")
        obj._on_trait_change(function_listener_3, "ok", dispatch="extended")
        obj._on_trait_change(function_listener_4, "ok", dispatch="extended")

        obj.ok = 2
        obj.ok = 3

        expected_1 = [2, 3]
        self.assertEqual(expected_1, calls_1)

        expected_2 = [("ok", 2), ("ok", 3)]
        self.assertEqual(expected_2, calls_2)

        expected_3 = [(obj, "ok", 2), (obj, "ok", 3)]
        self.assertEqual(expected_3, calls_3)

        expected_4 = [(obj, "ok", 0, 2), (obj, "ok", 2, 3)]
        self.assertEqual(expected_4, calls_4)

    def test_extended_notifiers_functions_failing(self):
        obj = ExtendedNotifiers()

        obj._on_trait_change(
            failing_function_listener_0, "fail", dispatch="extended"
        )
        obj._on_trait_change(
            failing_function_listener_1, "fail", dispatch="extended"
        )
        obj._on_trait_change(
            failing_function_listener_2, "fail", dispatch="extended"
        )
        obj._on_trait_change(
            failing_function_listener_3, "fail", dispatch="extended"
        )
        obj._on_trait_change(
            failing_function_listener_4, "fail", dispatch="extended"
        )

        obj.fail = 1

        six.assertCountEqual(self, [0, 1, 2, 3, 4], obj.exceptions_from)
        # 10 failures: 5 are from the internal extended listeners, see
        # test_extended_notifiers_methods_failing
        self.assertEqual([(obj, "fail", 0, 1)] * 10, self.exceptions)
