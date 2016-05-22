""" Tests for the dynamic notifiers. """
import gc

from traits import _py2to3

from traits.api import Event, Float, HasTraits, List, on_trait_change
from traits.testing.unittest_tools import unittest

from traits import trait_notifiers


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

    @on_trait_change('ok')
    def method_listener_0(self):
        self.rebind_calls_0.append(True)

    @on_trait_change('ok')
    def method_listener_1(self, new):
        self.rebind_calls_1.append(new)

    @on_trait_change('ok')
    def method_listener_2(self, name, new):
        self.rebind_calls_2.append((name, new))

    @on_trait_change('ok')
    def method_listener_3(self, obj, name, new):
        self.rebind_calls_3.append((obj, name, new))

    @on_trait_change('ok')
    def method_listener_4(self, obj, name, old, new):
        self.rebind_calls_4.append((obj, name, old, new))

    #### 'fail' trait listeners

    @on_trait_change('fail')
    def failing_method_listener_0(self):
        self.exceptions_from.append(0)
        raise Exception('error')

    @on_trait_change('fail')
    def failing_method_listener_1(self, new):
        self.exceptions_from.append(1)
        raise Exception('error')

    @on_trait_change('fail')
    def failing_method_listener_2(self, name, new):
        self.exceptions_from.append(2)
        raise Exception('error')

    @on_trait_change('fail')
    def failing_method_listener_3(self, obj, name, new):
        self.exceptions_from.append(3)
        raise Exception('error')

    @on_trait_change('fail')
    def failing_method_listener_4(self, obj, name, old, new):
        self.exceptions_from.append(4)
        raise Exception('error')

    def low_priority_first(self):
        self.prioritized_notifications.append(0)

    def high_priority_first(self):
        self.prioritized_notifications.append(1)

    def low_priority_second(self):
        self.prioritized_notifications.append(2)

    def high_priority_second(self):
        self.prioritized_notifications.append(3)

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
    raise Exception('error')


def failing_function_listener_1(new):
    exceptions_from.append(1)
    raise Exception('error')


def failing_function_listener_2(name, new):
    exceptions_from.append(2)
    raise Exception('error')


def failing_function_listener_3(obj, name, new):
    exceptions_from.append(3)
    raise Exception('error')


def failing_function_listener_4(obj, name, old, new):
    exceptions_from.append(4)
    raise Exception('error')


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

        expected_2 = [('ok', 2), ('ok', 3)]
        self.assertEqual(expected_2, obj.rebind_calls_2)

        expected_3 = [(obj, 'ok', 2), (obj, 'ok', 3)]
        self.assertEqual(expected_3, obj.rebind_calls_3)

        expected_4 = [(obj, 'ok', 0, 2), (obj, 'ok', 2, 3)]
        self.assertEqual(expected_4, obj.rebind_calls_4)

    def test_dynamic_notifiers_methods_failing(self):
        obj = DynamicNotifiers()
        obj.fail = 1

        _py2to3.assertCountEqual(self, [0, 1, 2, 3, 4], obj.exceptions_from)
        self.assertEqual([(obj, 'fail', 0, 1)]*5, self.exceptions)

    def test_dynamic_notifiers_functions(self):
        obj = DynamicNotifiers()

        obj.on_trait_change(function_listener_0, 'ok')
        obj.on_trait_change(function_listener_1, 'ok')
        obj.on_trait_change(function_listener_2, 'ok')
        obj.on_trait_change(function_listener_3, 'ok')
        obj.on_trait_change(function_listener_4, 'ok')

        obj.ok = 2
        obj.ok = 3

        expected_1 = [2, 3]
        self.assertEqual(expected_1, calls_1)

        expected_2 = [('ok', 2), ('ok', 3)]
        self.assertEqual(expected_2, calls_2)

        expected_3 = [(obj, 'ok', 2), (obj, 'ok', 3)]
        self.assertEqual(expected_3, calls_3)

        expected_4 = [(obj, 'ok', 0, 2), (obj, 'ok', 2, 3)]
        self.assertEqual(expected_4, calls_4)

    def test_priority_notifiers_first(self):

        obj = DynamicNotifiers()

        expected_high = set([1, 3])
        expected_low = set([0, 2])

        obj.on_trait_change(obj.low_priority_first, 'priority_test')
        obj.on_trait_change(obj.high_priority_first, 'priority_test',
                            priority=True)
        obj.on_trait_change(obj.low_priority_second, 'priority_test')
        obj.on_trait_change(obj.high_priority_second, 'priority_test',
                            priority=True)

        obj.priority_test = None

        high = set(obj.prioritized_notifications[:2])
        low = set(obj.prioritized_notifications[2:])

        self.assertSetEqual(expected_high, high)
        self.assertSetEqual(expected_low, low)


    def test_dynamic_notifiers_functions_failing(self):
        obj = DynamicNotifiers()

        obj.on_trait_change(failing_function_listener_0, 'fail')
        obj.on_trait_change(failing_function_listener_1, 'fail')
        obj.on_trait_change(failing_function_listener_2, 'fail')
        obj.on_trait_change(failing_function_listener_3, 'fail')
        obj.on_trait_change(failing_function_listener_4, 'fail')

        obj.fail = 1

        _py2to3.assertCountEqual(self, [0, 1, 2, 3, 4], obj.exceptions_from)
        # 10 failures: 5 are from the internal dynamic listeners, see
        # test_dynamic_notifiers_methods_failing
        self.assertEqual([(obj, 'fail', 0, 1)] * 10, self.exceptions)

    def test_object_can_be_garbage_collected(self):
        # Make sure that a trait object can be garbage collected even though
        # there are listener to its traits.

        import weakref

        obj = DynamicNotifiers()
        obj.on_trait_change(function_listener_0, 'ok')

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

    def test_creating_notifiers_dont_create_cyclic_garbage(self):
        gc.collect()
        DynamicNotifiers()
        # When an object with dynamic listeners has no more references,
        # it should not create cyclic garbage.
        self.assertEqual(gc.collect(), 0)


if __name__ == '__main__':
    unittest.main()
