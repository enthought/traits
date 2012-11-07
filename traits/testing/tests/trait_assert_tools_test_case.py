#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#------------------------------------------------------------------------------
import unittest
from traits.api import HasTraits, Float, List, Bool, on_trait_change
from traits.testing.api import TraitAssertTools


class MyClass(HasTraits):

    number = Float(2.0)
    list_of_numbers = List(Float)
    flag = Bool

    @on_trait_change('number')
    def _add_number_to_list(self, value):
        self.list_of_numbers.append(value)

    def add_to_number(self, value):
        self.number += value


class TraitAssertToolsTestCase(unittest.TestCase, TraitAssertTools):

    def setUp(self):
        self.my_class = MyClass()

    def test_when_using_with(self):
        """ Check normal use cases as a context manager.
        """
        my_class = self.my_class

        # Change event should NOT BE detected
        with self.assertTraitDoesNotChange(my_class, 'number') as result:
            my_class.flag = True
            my_class.number = 2.0
        self.assertIsNone(result.event)
        self.assertEqual(result.events, [])

        msg = 'The assertion result is not None: {0}'.format(result.event)
        self.assertIsNone(result.event, msg=msg)

        # Change event should BE detected
        with self.assertTraitChanges(my_class, 'number') as result:
            my_class.flag = False
            my_class.number = 5.0

        expected = (my_class, 'number', 2.0, 5.0)
        self.assertSequenceEqual(expected, result.event)

        # Change event should BE detected exactly 2 times
        with self.assertTraitChanges(my_class, 'number', count=2) as result:
            my_class.flag = False
            my_class.number = 4.0
            my_class.number = 3.0

        expected = [(my_class, 'number', 5.0, 4.0),
                    (my_class, 'number', 4.0, 3.0)]
        self.assertSequenceEqual(expected, result.events)
        self.assertSequenceEqual(expected[-1], result.event)

        # Change event should BE detected
        with self.assertTraitChanges(my_class, 'number') as result:
            my_class.flag = True
            my_class.add_to_number(10.0)

        expected = (my_class, 'number', 3.0, 13.0)
        self.assertSequenceEqual(expected, result.event)

        # Change event should BE detected exactly 3 times
        with self.assertTraitChanges(my_class, 'number', count=3) as result:
            my_class.flag = True
            my_class.add_to_number(10.0)
            my_class.add_to_number(10.0)
            my_class.add_to_number(10.0)

        expected = [(my_class, 'number', 13.0, 23.0),
                    (my_class, 'number', 23.0, 33.0),
                    (my_class, 'number', 33.0, 43.0)]
        self.assertSequenceEqual(expected, result.events)
        self.assertSequenceEqual(expected[-1], result.event)

    def test_indirect_events(self):
        """ Check catching indirect change events.
        """
        my_class = self.my_class

        # Change event should BE detected
        with self.assertTraitChanges(my_class, 'list_of_numbers[]') as \
                result:
            my_class.flag = True
            my_class.number = -3.0

        expected = (my_class, 'list_of_numbers_items', [], [-3.0])
        self.assertSequenceEqual(expected, result.event)

    def test_exception_inside_context(self):
        """ Check that exception inside the context statement block are
        propagated.

        """
        my_class = self.my_class

        with self.assertRaises(AttributeError):
            with self.assertTraitChanges(my_class, 'number'):
                my_class.i_do_exist

        with self.assertRaises(AttributeError):
            with self.assertTraitDoesNotChange(my_class, 'number'):
                my_class.i_do_exist

    def test_non_change_on_failure(self):
        """ Check behaviour when assertion should be raised for non trait
        change.

        """
        my_class = self.my_class
        traits = 'flag, number'
        with self.assertRaises(AssertionError):
            with self.assertTraitDoesNotChange(my_class, traits) as result:
                my_class.flag = True
                my_class.number = -3.0
        expected = [(my_class, 'flag', False, True),
                    (my_class, 'number', 2.0, -3.0)]
        self.assertEqual(result.events, expected)


    def test_change_on_failure(self):
        """ Check behaviour when assertion should be raised for trait change.
        """
        my_class = self.my_class
        with self.assertRaises(AssertionError):
            with self.assertTraitChanges(my_class, 'number') as result:
                my_class.flag = True
        self.assertEqual(result.events, [])

        # Change event will not be fired 3 times
        with self.assertRaises(AssertionError):
            with self.assertTraitChanges(my_class, 'number', count=3) as \
                    result:
                my_class.flag = True
                my_class.add_to_number(10.0)
                my_class.add_to_number(10.0)

        expected = [(my_class, 'number', 2.0, 12.0),
                    (my_class, 'number', 12.0, 22.0)]
        self.assertSequenceEqual(expected, result.events)
        self.assertSequenceEqual(expected[-1], result.event)

    def test_asserts_in_context_block(self):
        """ Make sure that the traits context manager does not stop
        regular assertions inside the managed code block from happening.
        """
        my_class = MyClass(number=16.0)

        with self.assertTraitDoesNotChange(my_class, 'number'):
            self.assertEqual(my_class.number, 16.0)

        with self.assertRaisesRegexp(AssertionError, '16\.0 != 12\.0'):
            with self.assertTraitDoesNotChange(my_class, 'number'):
                self.assertEqual(my_class.number, 12.0)

    def test_special_case_for_count(self):
        """ Count equal to 0 should be valid but it is discouraged.
        """
        my_class = MyClass(number=16.0)

        with self.assertTraitChanges(my_class, 'number', count=0):
            my_class.flag = True


if __name__ == '__main__':
    unittest.main()
