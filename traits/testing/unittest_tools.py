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
""" Trait assert mixin class to simplify test implementation for Trait
Classes.

"""

# Compatibility layer for Python 2.6: try loading unittest2
import sys
if sys.version_info[:2] == (2, 6):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest

else:
    import unittest


class _AssertTraitChangesContext(object):
    """ A context manager used to implement the trait change assert methods.

    Attributes
    ----------
    obj : HasTraits
        The HasTraits class instance who's class trait will change.

    xname : str
        The extended trait name of trait changes to listen too.

    count : int, optional
        The expected number of times the event should be fired. When None
        (default value) there is no check for the number of times the
        change event was fired.

    events : list of tuples
        A list with tuple elements containing the arguments of an
        `on_trait_change` event signature (<object>, <name>, <old>, <new>).

    Raises
    ------
    AssertionError :
          When the desired number of trait changed did not take place or when
          `count = None` and no trait change took place.

    """

    def __init__(self, obj, xname, count, test_case):
        """ Initialize the trait change assertion context manager.

        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance who's class trait will change.

        xname : str
            The extended trait name of trait changes to listen too.

        count : int, optional
            The expected number of times the event should be fired. When None
            (default value) there is no check for the number of times the
            change event was fired.

        test_case : TestCase
            A unittest TestCase where to raise the failureException if
            necessary.

        Notes
        -----
        - Checking if the provided xname corresponds to valid traits in
          the class is not implemented yet.

        """
        self.obj = obj
        self.xname = xname
        self.count = count
        self.events = []
        self.failureException = test_case.failureException

    def _listener(self, obj, name, old, new):
        """ Dummy trait listener
        """
        self.events.append((obj, name, old, new))

    def __enter__(self):
        """ Bind the trait listener
        """
        self.obj.on_trait_change(self._listener, self.xname)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """ Remove the trait listener

        """
        if exc_type is not None:
            return

        self.obj.on_trait_change(self._listener, self.xname, remove=True)
        if self.count is not None and len(self.events) != self.count:
            msg = 'Change event for {0} was fired {1} times instead of {2}'
            items = self.xname, len(self.events), self.count
            raise self.failureException(msg.format(*items))
        elif self.count is None and not self.events:
            msg = 'A change event was not fired for: {0}'.format(self.xname)
            raise self.failureException(msg)

class UnittestTools(object):
    """ Mixin class to augment the unittest.TestCase class with useful trait
    related assert methods.

    """

    def assertTraitChanges(self, obj, trait, count=None):
        """ Assert that the class trait changes exactly n times.

        Used in a with statement to assert that a class trait has changed
        during the execution of the code inside the with context block
        (similar to the assertRaises method).

        Please note that the context manager returns itself and the user can
        introspect the information of the fired events by accessing the
        ``events`` attribute of the context object. The attribute is a list
        with tuple elements containing the arguments of an `on_trait_change`
        event signature (<object>, <name>, <old>, <new>).

        **Example**::

            class MyClass(HasTraits):
               number = Float(2.0)

            my_class = MyClass()

            with self.assertTraitChanges(my_class, 'number') as ctx:
               my_class.number = 3.0

            self.assert(ctx.events, [(my_class, 'number', 2.0, 3.0)]

        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance who's class trait will change.

        xname : str
            The extended trait name of trait changes to listen too.

        count : int, optional
            The expected number of times the event should be fired. When None
            (default value) there is no check for the number of times the
            change event was fired.

        Notes
        -----
        - Checking if the provided xname corresponds to valid traits in
          the class is not implemented yet.

        """
        return _AssertTraitChangesContext(obj, trait, count, self)

    def assertTraitDoesNotChange(self, obj, xname):
        """ Assert that no trait event is fired.

        Used in a with statement to assert that a class trait has not changed
        during the execution of the code inside the with statement block.

        **Example**::

            class MyClass(HasTraits):
                number = Float(2.0)
                name = String

            my_class = MyClass()

            with self.assertTraitDoesNotChange(my_class, 'name'):
                 my_class.number = 2.0

        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance who's class trait will change.

        xname : str
            The extended trait name of trait changes to listen too.

        Notes
        -----
        - Checking if the provided xname corresponds to valid traits in
          the class is not implemented yet.

        """
        return _AssertTraitChangesContext(obj, xname, 0, self)
