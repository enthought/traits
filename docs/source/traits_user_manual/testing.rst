.. index:: testing, test trait classes

.. _testing_trait_classes:

======================
Testing Traits Classes
======================

A mixin class is provided to facilitate writing tests for HasTraits classes.
The methods :meth:`~traits.testing.api.UnittestTools.assertTraitChanges`
and :meth:`~traits.testing.api.UnittestTools.assertTraitDoesChange` are
available when the :class:`~traits.testing.api.UnittestTools` is added as
a mixin class in the developers TestCase.

The methods behave as a context manager and allow the developer to assert
that specific events have been fired and inspect the arguments that are passed
to the notification handlers at each event.

Both normal and extended trait names are supported. However, no check is
performed regarding the validity of the trait name, thus case is required to
safeguard against spelling mistakes in the names of the traits that we need
to assert the behaviour.

The following example demonstrates the basic usage of the mixin class in a
TestCase::

    import unittest
    from traits.api import HasTraits, Float, List, Bool, on_trait_change
    from traits.testing.api import UnittestTools


    class MyClass(HasTraits):

        number = Float(2.0)
        list_of_numbers = List(Float)
        flag = Bool

        @on_trait_change('number')
        def _add_number_to_list(self, value):
            """ Append the value to the list of numbers. """
            self.list_of_numbers.append(value)

        def add_to_number(self, value):
            """ Add the value to `number`. """
            self.number += value


    class MyTestCase(unittest.TestCase, UnittestTools):

        def setUp(self):
            self.my_class = MyClass()

        def test_when_using_with(self):
            """ Check normal use cases as a context manager.
            """
            my_class = self.my_class

            # Checking for change events
            with self.assertTraitChanges(my_class, 'number') as result:
                my_class.number = 5.0

            # Inspecting the last recorded event
            expected = (my_class, 'number', 2.0, 5.0)
            self.assertSequenceEqual(result.events, [expected])

            # Checking for specific number of events
            with self.assertTraitChanges(my_class, 'number', count=3) as result:
                my_class.flag = True
                my_class.add_to_number(10.0)
                my_class.add_to_number(10.0)
                my_class.add_to_number(10.0)

            expected = [(my_class, 'number', 5.0, 15.0),
                        (my_class, 'number', 15.0, 25.0),
                        (my_class, 'number', 25.0, 35.0)]
            self.assertSequenceEqual(result.events, expected)

            # Check using extended names
            with self.assertTraitChanges(my_class, 'list_of_numbers[]'):
                my_class.number = -3.0

            # Check that event is not fired
            my_class.number = 2.0
            with self.assertTraitDoesNotChange(my_class, 'number') as result:
                my_class.flag = True
                my_class.number = 2.0  # The value is the same as the original