# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for the dynamic notifiers. """
import gc
import unittest

from traits import trait_notifiers
from traits.api import Event, Float, HasTraits, List, on_trait_change


class DynamicNotifiers(HasTraits):

    ok = Float
    fail = Float
    priority_test = Event

    # Lists where we accumulate the arguments of calls to the traits notifiers.
    rebind_calls_0 = List
    rebind_calls_1 = List
    rebind_calls_2 = List
    rebind_calls_3 = List
    rebind_calls_4 = List
    exceptions_from = List
    prioritized_notifications = List

    #### 'ok' trait listeners

    @on_trait_change("ok")
    def method_listener_0(self):
        self.rebind_calls_0.append(True)

    @on_trait_change("ok")
    def method_listener_1(self, new):
        self.rebind_calls_1.append(new)

    @on_trait_change("ok")
    def method_listener_2(self, name, new):
        self.rebind_calls_2.append((name, new))

    @on_trait_change("ok")
    def method_listener_3(self, obj, name, new):
        self.rebind_calls_3.append((obj, name, new))

    @on_trait_change("ok")
    def method_listener_4(self, obj, name, old, new):
        self.rebind_calls_4.append((obj, name, old, new))

    #### 'fail' trait listeners

    @on_trait_change("fail")
    def failing_method_listener_0(self):
        self.exceptions_from.append(0)
        raise Exception("error")

    @on_trait_change("fail")
    def failing_method_listener_1(self, new):
        self.exceptions_from.append(1)
        raise Exception("error")

    @on_trait_change("fail")
    def failing_method_listener_2(self, name, new):
        self.exceptions_from.append(2)
        raise Exception("error")

    @on_trait_change("fail")
    def failing_method_listener_3(self, obj, name, new):
        self.exceptions_from.append(3)
        raise Exception("error")

    @on_trait_change("fail")
    def failing_method_listener_4(self, obj, name, old, new):
        self.exceptions_from.append(4)
        raise Exception("error")

    def low_priority_first(self):
        self.prioritized_notifications.append(0)

    def high_priority_first(self):
        self.prioritized_notifications.append(1)

    def low_priority_second(self):
        self.prioritized_notifications.append(2)

    def high_priority_second(self):
        self.prioritized_notifications.append(3)


class UnhashableDynamicNotifiers(DynamicNotifiers):
    """ Class that cannot be used as a key in a dictionary.
    """

    a_list = List

    def __hash__(self):
        raise NotImplementedError()

    def __eq__(self):
        raise NotImplementedError()


class TestDynamicNotifiers(unittest.TestCase):

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

    def test_dynamic_notifiers_methods(self):
        obj = DynamicNotifiers(ok=2)
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

    def test_dynamic_notifiers_methods_failing(self):
        obj = DynamicNotifiers()
        obj.fail = 1

        self.assertCountEqual([0, 1, 2, 3, 4], obj.exceptions_from)
        self.assertEqual([(obj, "fail", 0, 1)] * 5, self.exceptions)

    def test_dynamic_notifiers_functions(self):
        calls_0 = []

        def function_listener_0():
            calls_0.append(())

        calls_1 = []

        def function_listener_1(new):
            calls_1.append((new,))

        calls_2 = []

        def function_listener_2(name, new):
            calls_2.append((name, new))

        calls_3 = []

        def function_listener_3(obj, name, new):
            calls_3.append((obj, name, new))

        calls_4 = []

        def function_listener_4(obj, name, old, new):
            calls_4.append((obj, name, old, new))

        obj = DynamicNotifiers()

        obj.on_trait_change(function_listener_0, "ok")
        obj.on_trait_change(function_listener_1, "ok")
        obj.on_trait_change(function_listener_2, "ok")
        obj.on_trait_change(function_listener_3, "ok")
        obj.on_trait_change(function_listener_4, "ok")

        obj.ok = 2
        obj.ok = 3

        expected_0 = [(), ()]
        self.assertEqual(expected_0, calls_0)

        expected_1 = [(2.0,), (3.0,)]
        self.assertEqual(expected_1, calls_1)

        expected_2 = [("ok", 2.0), ("ok", 3.0)]
        self.assertEqual(expected_2, calls_2)

        expected_3 = [(obj, "ok", 2.0), (obj, "ok", 3.0)]
        self.assertEqual(expected_3, calls_3)

        expected_4 = [(obj, "ok", 0.0, 2.0), (obj, "ok", 2.0, 3.0)]
        self.assertEqual(expected_4, calls_4)

    def test_priority_notifiers_first(self):

        obj = DynamicNotifiers()

        expected_high = set([1, 3])
        expected_low = set([0, 2])

        obj.on_trait_change(obj.low_priority_first, "priority_test")
        obj.on_trait_change(
            obj.high_priority_first, "priority_test", priority=True
        )
        obj.on_trait_change(obj.low_priority_second, "priority_test")
        obj.on_trait_change(
            obj.high_priority_second, "priority_test", priority=True
        )

        obj.priority_test = None

        high = set(obj.prioritized_notifications[:2])
        low = set(obj.prioritized_notifications[2:])

        self.assertSetEqual(expected_high, high)
        self.assertSetEqual(expected_low, low)

    def test_dynamic_notifiers_functions_failing(self):
        obj = DynamicNotifiers()

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

        obj.on_trait_change(failing_function_listener_0, "fail")
        obj.on_trait_change(failing_function_listener_1, "fail")
        obj.on_trait_change(failing_function_listener_2, "fail")
        obj.on_trait_change(failing_function_listener_3, "fail")
        obj.on_trait_change(failing_function_listener_4, "fail")

        obj.fail = 1

        self.assertEqual([0, 1, 2, 3, 4], exceptions_from)
        self.assertCountEqual([0, 1, 2, 3, 4], obj.exceptions_from)
        # 10 failures: 5 are from the internal dynamic listeners, see
        # test_dynamic_notifiers_methods_failing
        self.assertEqual([(obj, "fail", 0, 1)] * 10, self.exceptions)

    def test_object_can_be_garbage_collected(self):
        # Make sure that a trait object can be garbage collected even though
        # there are listener to its traits.

        import weakref

        def listener():
            pass

        obj = DynamicNotifiers()
        obj.on_trait_change(listener, "ok")

        # Create a weak reference to `obj` with a callback that flags when the
        # object is finalized.
        obj_collected = []

        def obj_collected_callback(weakref):
            obj_collected.append(True)

        obj_weakref = weakref.ref(obj, obj_collected_callback)

        # Remove reference to `obj`, and check that the weak reference
        # callback has been called, indicating that it has been collected.
        del obj

        self.assertEqual(obj_collected, [True])
        self.assertIsNone(obj_weakref())

    def test_unhashable_object_can_be_garbage_collected(self):
        # Make sure that an unhashable trait object can be garbage collected
        # even though there are listener to its traits.

        import weakref

        def listener():
            pass

        obj = UnhashableDynamicNotifiers()
        obj.on_trait_change(listener, "a_list:ok")
        # Changing a List trait is the easiest way to trigger a check into the
        # weak key dict.
        obj.a_list.append(UnhashableDynamicNotifiers())

        # Create a weak reference to `obj` with a callback that flags when the
        # object is finalized.
        obj_collected = []

        def obj_collected_callback(weakref):
            obj_collected.append(True)

        obj_weakref = weakref.ref(obj, obj_collected_callback)

        # Remove reference to `obj`, and check that the weak reference
        # callback has been called, indicating that it has been collected.
        del obj

        self.assertEqual(obj_collected, [True])
        self.assertIsNone(obj_weakref())

    def test_creating_notifiers_dont_create_cyclic_garbage(self):
        gc.collect()
        DynamicNotifiers()
        # When an object with dynamic listeners has no more references,
        # it should not create cyclic garbage.
        self.assertEqual(gc.collect(), 0)
