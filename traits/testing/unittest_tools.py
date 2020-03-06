# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Trait assert mixin class to simplify test implementation for Trait
Classes.

"""

import contextlib
import threading
import sys
import warnings

# Support for 'from traits.testing.unittest_tools import unittest',
# which was used to make unittest2 available under the name unittest
# on Python 2.6. We keep the import for now, for backwards compatibility.
import unittest  # noqa: F401

from traits.api import (
    Any,
    Event,
    HasStrictTraits,
    Instance,
    Int,
    List,
    Str,
    Property,
)
from traits.util.async_trait_wait import wait_for_condition


class _AssertTraitChangesContext(object):
    """ A context manager used to implement the trait change assert methods.

    Notes
    -----
    Checking if the provided xname corresponds to valid traits in the class
    is not implemented yet.

    Parameters
    ----------
    obj : HasTraits
        The HasTraits class instance whose class trait will change.

    xname : str
        The extended trait name of trait changes to listen to.

    count : int, optional
        The expected number of times the event should be fired. When None
        (default value) there is no check for the number of times the
        change event was fired.

    test_case : TestCase
        A unittest TestCase where to raise the failureException if
        necessary.

    Attributes
    ----------
    obj : HasTraits
        The HasTraits class instance whose class trait will change.

    xname : str
        The extended trait name of trait changes to listen to.

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
        self.obj = obj
        self.xname = xname
        self.count = count
        self.event = None
        self.events = []
        self.failureException = test_case.failureException

    def _listener(self, obj, name, old, new):
        """ Dummy trait listener.
        """
        self.event = (obj, name, old, new)
        self.events.append(self.event)

    def __enter__(self):
        """ Bind the trait listener.
        """
        self.obj.on_trait_change(self._listener, self.xname)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """ Remove the trait listener.
        """
        if exc_type is not None:
            return False

        self.obj.on_trait_change(self._listener, self.xname, remove=True)
        if self.count is not None and len(self.events) != self.count:
            msg = "Change event for {0} was fired {1} times instead of {2}"
            items = self.xname, len(self.events), self.count
            raise self.failureException(msg.format(*items))
        elif self.count is None and not self.events:
            msg = "A change event was not fired for: {0}".format(self.xname)
            raise self.failureException(msg)
        return False


@contextlib.contextmanager
def reverse_assertion(context, msg):
    context.__enter__()
    try:
        yield context
    finally:
        try:
            context.__exit__(None, None, None)
        except AssertionError:
            pass
        else:
            raise context.failureException(msg)


class _TraitsChangeCollector(HasStrictTraits):
    """ Class allowing thread-safe recording of events.
    """

    # The object we're listening to.
    obj = Any

    # The (possibly extended) trait name(s).
    trait_name = Str

    # Read-only event count.
    event_count = Property(Int)

    # Event that's triggered when the event count is updated.
    event_count_updated = Event

    # Private list of events.
    events = List(Any)

    # Lock used to allow access to events by multiple threads
    # simultaneously.
    _lock = Instance(threading.Lock, ())

    def __init__(self, **traits):
        if "trait" in traits:
            value = traits.pop("trait")
            message = (
                "The `trait` keyword is deprecated." " please use `trait_name`"
            )
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            traits["trait_name"] = value
        super(_TraitsChangeCollector, self).__init__(**traits)

    def start_collecting(self):
        self.obj.on_trait_change(self._event_handler, self.trait_name)

    def stop_collecting(self):
        self.obj.on_trait_change(
            self._event_handler, self.trait_name, remove=True
        )

    def _event_handler(self, new):
        with self._lock:
            self.events.append(new)
        self.event_count_updated = True

    def _get_event_count(self):
        """ Traits property getter.

        Thread-safe access to event count.

        """
        with self._lock:
            return len(self.events)


class UnittestTools(object):
    """ Mixin class to augment the unittest.TestCase class with useful trait
    related assert methods.

    """

    def assertTraitChanges(
        self, obj, trait, count=None, callableObj=None, *args, **kwargs
    ):
        """ Assert an object trait changes a given number of times.

        Assert that the class trait changes exactly `count` times during
        execution of the provided function.

        This method can also be used in a with statement to assert that
        a class trait has changed during the execution of the code inside
        the with statement (similar to the assertRaises method). Please note
        that in that case the context manager returns itself and the user
        can introspect the information of:

        - The last event fired by accessing the ``event`` attribute of the
          returned object.

        - All the fired events by accessing the ``events`` attribute of
          the return object.

        Note that in the case of chained properties (trait 'foo' depends on
        'bar', which in turn depends on 'baz'), the order in which the
        corresponding trait events appear in the ``events`` attribute is
        not well-defined, and may depend on dictionary ordering.

        **Example**::

            class MyClass(HasTraits):
                number = Float(2.0)

            my_class = MyClass()

            with self.assertTraitChanges(my_class, 'number', count=1):
                my_class.number = 3.0

        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance whose class trait will change.

        trait : str
            The extended trait name of trait changes to listen to.

        count : int or None, optional
            The expected number of times the event should be fired. When None
            (default value) there is no check for the number of times the
            change event was fired.

        callableObj : callable, optional
            A callable object that will trigger the expected trait change.
            When None (default value) a trigger is expected to be called
            under the context manger returned by this method.

        *args :
            List of positional arguments for ``callableObj``

        **kwargs :
            Dict of keyword value pairs to be passed to the ``callableObj``


        Returns
        -------
        context : context manager or None
            If ``callableObj`` is None, an assertion context manager is
            returned, inside of which a trait-change trigger can be invoked.
            Otherwise, the context is used internally with ``callableObj`` as
            the trigger, in which case None is returned.

        Notes
        -----
        - Checking if the provided ``trait`` corresponds to valid traits in
          the class is not implemented yet.
        - Using the functional version of the assert method requires the
          ``count`` argument to be given even if it is None.

        """
        context = _AssertTraitChangesContext(obj, trait, count, self)
        if callableObj is None:
            return context
        with context:
            callableObj(*args, **kwargs)

    def assertTraitDoesNotChange(
        self, obj, trait, callableObj=None, *args, **kwargs
    ):
        """ Assert an object trait does not change.

        Assert that the class trait does not change during
        execution of the provided function.

        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance whose class trait will change.

        trait : str
            The extended trait name of trait changes to listen to.

        callableObj : callable, optional
            A callable object that should not trigger a change in the
            passed trait.  When None (default value) a trigger is expected
            to be called under the context manger returned by this method.

        *args :
            List of positional arguments for ``callableObj``

        **kwargs :
            Dict of keyword value pairs to be passed to the ``callableObj``


        Returns
        -------
        context : context manager or None
            If ``callableObj`` is None, an assertion context manager is
            returned, inside of which a trait-change trigger can be invoked.
            Otherwise, the context is used internally with ``callableObj`` as
            the trigger, in which case None is returned.

        """
        msg = "A change event was fired for: {0}".format(trait)
        context = _AssertTraitChangesContext(obj, trait, None, self)
        if callableObj is None:
            return reverse_assertion(context, msg)
        with reverse_assertion(context, msg):
            callableObj(*args, **kwargs)

    @contextlib.contextmanager
    def assertMultiTraitChanges(
        self, objects, traits_modified, traits_not_modified
    ):
        """ Assert that traits on multiple objects do or do not change.

        This combines some of the functionality of `assertTraitChanges` and
        `assertTraitDoesNotChange`.

        Parameters
        ----------
        objects : list of HasTraits
            The HasTraits class instances whose traits will change.

        traits_modified : list of str
            The extended trait names of trait expected to change.

        traits_not_modified : list of str
            The extended trait names of traits not expected to change.

        """
        with contextlib.ExitStack() as exit_stack:
            cms = []
            for obj in objects:
                for trait in traits_modified:
                    cms.append(exit_stack.enter_context(
                        self.assertTraitChanges(obj, trait)))
                for trait in traits_not_modified:
                    cms.append(exit_stack.enter_context(
                        self.assertTraitDoesNotChange(obj, trait)))
            yield tuple(cms)

    @contextlib.contextmanager
    def assertTraitChangesAsync(self, obj, trait, count=1, timeout=5.0):
        """ Assert an object trait eventually changes.

        Context manager used to assert that the given trait changes at
        least `count` times within the given timeout, as a result of
        execution of the body of the corresponding with block.

        The trait changes are permitted to occur asynchronously.

        **Example usage**::

            with self.assertTraitChangesAsync(my_object, 'SomeEvent', count=4):
                <do stuff that should cause my_object.SomeEvent to be
                fired at least 4 times within the next 5 seconds>


        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance whose class trait will change.

        trait : str
            The extended trait name of trait changes to listen to.

        count : int, optional
            The expected number of times the event should be fired.

        timeout : float or None, optional
            The amount of time in seconds to wait for the specified number
            of changes. None can be used to indicate no timeout.

        """
        collector = _TraitsChangeCollector(obj=obj, trait_name=trait)

        # Pass control to body of the with statement.
        collector.start_collecting()
        try:
            yield collector

            # Wait for the expected number of events to arrive.
            try:
                wait_for_condition(
                    condition=lambda obj: obj.event_count >= count,
                    obj=collector,
                    trait="event_count_updated",
                    timeout=timeout,
                )
            except RuntimeError:
                actual_event_count = collector.event_count
                msg = (
                    "Expected {0} event on {1} to be fired at least {2} "
                    "times, but the event was only fired {3} times "
                    "before timeout ({4} seconds)."
                ).format(trait, obj, count, actual_event_count, timeout)
                self.fail(msg)

        finally:
            collector.stop_collecting()

    def assertEventuallyTrue(self, obj, trait, condition, timeout=5.0):
        """ Assert that the given condition is eventually true.

        Parameters
        ----------
        obj : HasTraits
            The HasTraits class instance whose traits will change.

        trait : str
            The extended trait name of trait changes to listen to.

        condition : callable
            A function that will be called when the specified trait
            changes.  This should accept ``obj`` and should return a
            Boolean indicating whether the condition is satisfied or not.

        timeout : float or None, optional
            The amount of time in seconds to wait for the condition to
            become true.  None can be used to indicate no timeout.

        """
        try:
            wait_for_condition(
                condition=condition, obj=obj, trait=trait, timeout=timeout
            )
        except RuntimeError:
            # Helpful to know whether we timed out because the
            # condition never became true, or because the expected
            # event was never issued.
            condition_at_timeout = condition(obj)
            self.fail(
                "Timed out waiting for condition. "
                "At timeout, condition was {0}.".format(condition_at_timeout)
            )

    @contextlib.contextmanager
    def _catch_warnings(self):
        # Ugly hack copied from the core Python code (see
        # Lib/test/test_support.py) to reset the warnings registry
        # for the module making use of this context manager.
        #
        # Note that this hack is unnecessary in Python 3.4 and later; see
        # http://bugs.python.org/issue4180 for the background.
        registry = sys._getframe(4).f_globals.get("__warningregistry__")
        if registry:
            registry.clear()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)
            yield w

    @contextlib.contextmanager
    def assertDeprecated(self):
        """
        Assert that the code inside the with block is deprecated.  Intended
        for testing uses of traits.util.deprecated.deprecated.

        """
        with self._catch_warnings() as w:
            yield w
        self.assertGreater(
            len(w),
            0,
            msg="Expected a DeprecationWarning, " "but none was issued",
        )

    @contextlib.contextmanager
    def assertNotDeprecated(self):
        """
        Assert that the code inside the with block is not deprecated.  Intended
        for testing uses of traits.util.deprecated.deprecated.

        """
        with self._catch_warnings() as w:
            yield w
        self.assertEqual(
            len(w),
            0,
            msg="Expected no DeprecationWarning, "
            "but at least one was issued",
        )
