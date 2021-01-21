.. index:: testing, test trait classes

Testing
=======

.. _testing_trait_classes:

Testing Traits Classes
----------------------

A mixin class is provided to facilitate writing tests for HasTraits classes.
The following methods are available when |UnittestTools| is added as a
mixin class in the developer's test cases.

.. autosummary::
    :nosignatures:

    ~traits.testing.unittest_tools.UnittestTools.assertTraitChanges
    ~traits.testing.unittest_tools.UnittestTools.assertTraitDoesNotChange
    ~traits.testing.unittest_tools.UnittestTools.assertMultiTraitChanges
    ~traits.testing.unittest_tools.UnittestTools.assertTraitChangesAsync
    ~traits.testing.unittest_tools.UnittestTools.assertEventuallyTrue

The above assert methods, except |assertEventuallyTrue|, can be used as
context managers, which at entry, hook a trait listeners on the class for the
desired events and record the arguments passed to the change handler at every
fired event. This way the developer can easily assert that specific events
have been fired. Further analysis and checking can be performed by inspecting
the list of recorded events. Both normal and extended trait names are
supported. However, no check is performed regarding the validity of the trait
name, thus care is required to safeguard against spelling mistakes in the
names of the traits that we need to assert the behaviour.

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

Using Mocks
-----------

Trying to mock a method in a |HasStrictTraits| instance will raise an error
because the |HasStrictTraits| machinery does not allow any modification of
the methods and attributes of a |HasStrictTraits| instance. To circumvent the
|HasStrictTraits| machinery, and mock methods using ``unittest.mock`` or
`the mock library`_, please follow the logic in the example below::

    from traits.api import HasStrictTraits, Float
    from unittest.mock import Mock

    class MyClass(HasStrictTraits):

        number = Float(2.0)

        def add_to_number(self, value):
            """ Add the value to `number`. """
            self.number += value

    my_class = MyClass()

    # Using my_class.add_to_number = Mock() will fail.
    # But setting the mock on the instance `__dict__` works.
    my_class.__dict__['add_to_number'] = Mock()

    # We can now use the mock in our tests.
    my_class.add_to_number(42)
    print(my_class.add_to_number.call_args_list)

.. note::

    The above method will not work for mocking |Property| setters,
    getters and validators.

.. _the mock library: https://pypi.python.org/pypi/mock
.. |HasStrictTraits| replace:: :class:`~traits.has_traits.HasStrictTraits`
.. |UnittestTools| replace:: :class:`~traits.testing.unittest_tools.UnittestTools`
.. |Property| replace:: :func:`~traits.traits.Property`
.. |assertEventuallyTrue| replace:: :func:`~traits.testing.unittest_tools.UnittestTools.assertEventuallyTrue`
