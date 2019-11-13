# ------------------------------------------------------------------------------
# Copyright (c) 2005-2013, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# ------------------------------------------------------------------------------
import threading
import time
import warnings

import six
import six.moves as sm

from traits.api import (
    Bool,
    Event,
    Float,
    HasTraits,
    Int,
    List,
    on_trait_change,
)
from traits.testing.api import UnittestTools
# unittest_tools provides a reference to unittest for historical reasons, and
# downstream packages may still be doing "from traits.testing.unittest_tools
# import unittest". We keep this import as-is (instead of doing a simple
# "import unittest") to make sure we don't break those packages.
from traits.testing.unittest_tools import unittest
from traits.util.api import deprecated


@deprecated("This function is outdated. Use 'shiny' instead!")
def old_and_dull():
    """ A deprecated function, for use in assertDeprecated tests.

    """
    pass


class TestObject(HasTraits):

    number = Float(2.0)
    list_of_numbers = List(Float)
    flag = Bool

    @on_trait_change("number")
    def _add_number_to_list(self, value):
        self.list_of_numbers.append(value)

    def add_to_number(self, value):
        self.number += value


class UnittestToolsTestCase(unittest.TestCase, UnittestTools):
    def setUp(self):
        self.test_object = TestObject()

    def test_when_using_with(self):
        """ Check normal use cases as a context manager.
        """
        test_object = self.test_object

        # Change event should NOT BE detected
        with self.assertTraitDoesNotChange(test_object, "number") as result:
            test_object.flag = True
            test_object.number = 2.0

        msg = "The assertion result is not None: {0}".format(result.event)
        self.assertIsNone(result.event, msg=msg)

        # Change event should BE detected
        with self.assertTraitChanges(test_object, "number") as result:
            test_object.flag = False
            test_object.number = 5.0

        expected = (test_object, "number", 2.0, 5.0)
        self.assertSequenceEqual(expected, result.event)

        # Change event should BE detected exactly 2 times
        with self.assertTraitChanges(test_object, "number", count=2) as result:
            test_object.flag = False
            test_object.number = 4.0
            test_object.number = 3.0

        expected = [
            (test_object, "number", 5.0, 4.0),
            (test_object, "number", 4.0, 3.0),
        ]
        self.assertSequenceEqual(expected, result.events)
        self.assertSequenceEqual(expected[-1], result.event)

        # Change event should BE detected
        with self.assertTraitChanges(test_object, "number") as result:
            test_object.flag = True
            test_object.add_to_number(10.0)

        expected = (test_object, "number", 3.0, 13.0)
        self.assertSequenceEqual(expected, result.event)

        # Change event should BE detected exactly 3 times
        with self.assertTraitChanges(test_object, "number", count=3) as result:
            test_object.flag = True
            test_object.add_to_number(10.0)
            test_object.add_to_number(10.0)
            test_object.add_to_number(10.0)

        expected = [
            (test_object, "number", 13.0, 23.0),
            (test_object, "number", 23.0, 33.0),
            (test_object, "number", 33.0, 43.0),
        ]
        self.assertSequenceEqual(expected, result.events)
        self.assertSequenceEqual(expected[-1], result.event)

    def test_assert_multi_changes(self):
        test_object = self.test_object

        # Change event should NOT BE detected
        with self.assertMultiTraitChanges(
            [test_object], [], ["flag", "number", "list_of_numbers[]"]
        ) as results:
            test_object.number = 2.0

        events = list(filter(bool, (result.event for result in results)))
        msg = "The assertion result is not None: {0}".format(", ".join(events))
        self.assertFalse(events, msg=msg)

        # Change event should BE detected
        with self.assertMultiTraitChanges(
            [test_object], ["number", "list_of_numbers[]"], ["flag"]
        ) as results:
            test_object.number = 5.0

        events = list(filter(bool, (result.event for result in results)))
        msg = "The assertion result is None"
        self.assertTrue(events, msg=msg)

    def test_when_using_functions(self):
        test_object = self.test_object

        # Change event should BE detected
        self.assertTraitChanges(
            test_object, "number", 1, test_object.add_to_number, 13.0
        )

        # Change event should NOT BE detected
        self.assertTraitDoesNotChange(
            test_object, "flag", test_object.add_to_number, 13.0
        )

    def test_indirect_events(self):
        """ Check catching indirect change events.
        """
        test_object = self.test_object

        # Change event should BE detected
        with self.assertTraitChanges(
            test_object, "list_of_numbers[]"
        ) as result:
            test_object.flag = True
            test_object.number = -3.0

        expected = (test_object, "list_of_numbers_items", [], [-3.0])
        self.assertSequenceEqual(expected, result.event)

    def test_exception_inside_context(self):
        """ Check that exception inside the context statement block are
        propagated.

        """
        test_object = self.test_object

        with self.assertRaises(AttributeError):
            with self.assertTraitChanges(test_object, "number"):
                test_object.i_do_exist

        with self.assertRaises(AttributeError):
            with self.assertTraitDoesNotChange(test_object, "number"):
                test_object.i_do_exist

    def test_non_change_on_failure(self):
        """ Check behaviour when assertion should be raised for non trait
        change.

        """
        test_object = self.test_object
        traits = "flag, number"
        with self.assertRaises(AssertionError):
            with self.assertTraitDoesNotChange(test_object, traits) as result:
                test_object.flag = True
                test_object.number = -3.0
        expected = [
            (test_object, "flag", False, True),
            (test_object, "number", 2.0, -3.0),
        ]
        self.assertEqual(result.events, expected)

    def test_change_on_failure(self):
        """ Check behaviour when assertion should be raised for trait change.
        """
        test_object = self.test_object
        with self.assertRaises(AssertionError):
            with self.assertTraitChanges(test_object, "number") as result:
                test_object.flag = True
        self.assertEqual(result.events, [])

        # Change event will not be fired 3 times
        with self.assertRaises(AssertionError):
            with self.assertTraitChanges(
                test_object, "number", count=3
            ) as result:
                test_object.flag = True
                test_object.add_to_number(10.0)
                test_object.add_to_number(10.0)

        expected = [
            (test_object, "number", 2.0, 12.0),
            (test_object, "number", 12.0, 22.0),
        ]
        self.assertSequenceEqual(expected, result.events)

    def test_asserts_in_context_block(self):
        """ Make sure that the traits context manager does not stop
        regular assertions inside the managed code block from happening.
        """
        test_object = TestObject(number=16.0)

        with self.assertTraitDoesNotChange(test_object, "number"):
            self.assertEqual(test_object.number, 16.0)

        with six.assertRaisesRegex(self, AssertionError, r"16\.0 != 12\.0"):
            with self.assertTraitDoesNotChange(test_object, "number"):
                self.assertEqual(test_object.number, 12.0)

    def test_special_case_for_count(self):
        """ Count equal to 0 should be valid but it is discouraged.
        """
        test_object = TestObject(number=16.0)

        with self.assertTraitChanges(test_object, "number", count=0):
            test_object.flag = True

    def test_assert_trait_changes_async(self):
        # Exercise assertTraitChangesAsync.
        thread_count = 10
        events_per_thread = 1000

        class A(HasTraits):
            event = Event

        a = A()

        def thread_target(obj, count):
            "Fire obj.event 'count' times."
            for _ in sm.range(count):
                obj.event = True

        threads = [
            threading.Thread(target=thread_target, args=(a, events_per_thread))
            for _ in sm.range(thread_count)
        ]

        expected_count = thread_count * events_per_thread
        with self.assertTraitChangesAsync(
            a, "event", expected_count, timeout=60.0
        ):
            for t in threads:
                t.start()

        for t in threads:
            t.join()

    def test_assert_trait_changes_async_events(self):
        # Check access to the events after the with
        # block completes.
        thread_count = 10
        events_per_thread = 100

        class A(HasTraits):
            event = Event(Int)

        a = A()

        def thread_target(obj, count):
            "Fire obj.event 'count' times."
            for n in sm.range(count):
                time.sleep(0.001)
                obj.event = n

        threads = [
            threading.Thread(target=thread_target, args=(a, events_per_thread))
            for _ in sm.range(thread_count)
        ]

        expected_count = thread_count * events_per_thread
        with self.assertTraitChangesAsync(
            a, "event", expected_count, timeout=60.0
        ) as event_collector:
            for t in threads:
                t.start()

        for t in threads:
            t.join()

        six.assertCountEqual(
            self,
            event_collector.events,
            list(sm.range(events_per_thread)) * thread_count,
        )

    def test_assert_trait_changes_async_failure(self):
        # Exercise assertTraitChangesAsync.
        thread_count = 10
        events_per_thread = 10000

        class A(HasTraits):
            event = Event

        a = A()

        def thread_target(obj, count):
            "Fire obj.event 'count' times."
            for _ in sm.range(count):
                obj.event = True

        threads = [
            threading.Thread(target=thread_target, args=(a, events_per_thread))
            for _ in sm.range(thread_count)
        ]

        expected_count = thread_count * events_per_thread
        with self.assertRaises(AssertionError):
            with self.assertTraitChangesAsync(a, "event", expected_count + 1):
                for t in threads:
                    t.start()

        for t in threads:
            t.join()

    def test_assert_eventually_true_fails_on_timeout(self):
        class A(HasTraits):
            foo = Bool(False)

        a = A()

        def condition(a_object):
            return a_object.foo

        with self.assertRaises(self.failureException):
            self.assertEventuallyTrue(
                condition=condition, obj=a, trait="foo", timeout=1.0
            )

    def test_assert_eventually_true_passes_when_condition_becomes_true(self):
        class A(HasTraits):
            foo = Bool(False)

        def condition(a_object):
            return a_object.foo

        a = A()

        def thread_target(a):
            time.sleep(1.0)
            a.foo = True

        t = threading.Thread(target=thread_target, args=(a,))
        t.start()
        self.assertEventuallyTrue(
            condition=condition, obj=a, trait="foo", timeout=10.0
        )
        t.join()

    def test_assert_eventually_true_passes_when_condition_starts_true(self):
        class A(HasTraits):
            foo = Bool(True)

        def condition(a_object):
            return a_object.foo

        a = A()
        self.assertEventuallyTrue(
            condition=condition, obj=a, trait="foo", timeout=10.0
        )

    def test_assert_deprecated(self):
        with self.assertDeprecated():
            old_and_dull()

    def test_assert_deprecated_failures(self):
        with self.assertRaises(self.failureException):
            with self.assertDeprecated():
                pass

    def test_assert_deprecated_when_warning_already_issued(self):
        # Exercise a problematic case where previous calls to a function or
        # method that issues a DeprecationWarning have already polluted the
        # __warningregistry__.  For this, we need a single call-point to
        # old_and_dull, since distinct call-points have separate entries in
        # __warningregistry__.
        def old_and_dull_caller():
            old_and_dull()

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always", DeprecationWarning)

            # Pollute the registry by pre-calling the function.
            old_and_dull_caller()

            # Check that we can still detect the DeprecationWarning.
            with self.assertDeprecated():
                old_and_dull_caller()

    def test_assert_not_deprecated_failures(self):
        with self.assertRaises(self.failureException):
            with self.assertNotDeprecated():
                old_and_dull()

    def test_assert_not_deprecated(self):
        with self.assertNotDeprecated():
            pass

    def test_assert_not_deprecated_when_warning_already_issued(self):
        # Exercise a problematic case where previous calls to a function or
        # method that issues a DeprecationWarning have already polluted the
        # __warningregistry__.  For this, we need a single call-point to
        # old_and_dull, since distinct call-points have separate entries in
        # __warningregistry__.
        def old_and_dull_caller():
            old_and_dull()

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always", DeprecationWarning)

            # Pollute the registry by pre-calling the function.
            old_and_dull_caller()

            # Check that we can still detect the DeprecationWarning.
            with self.assertRaises(self.failureException):
                with self.assertNotDeprecated():
                    old_and_dull_caller()
