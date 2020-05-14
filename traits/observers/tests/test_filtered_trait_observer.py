# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.has_traits import HasTraits
from traits.trait_base import Undefined, Uninitialized
from traits.trait_types import Float, Instance, Int, List
from traits.observers._filtered_trait_observer import FilteredTraitObserver
from traits.observers._testing import (
    call_add_or_remove_notifiers,
    create_graph,
    DummyNotifier,
    DummyObservable,
    DummyObserver,
)


class DummyFilter:
    """ A callable to be used as the 'filter' for FilteredTraitObserver
    """

    def __init__(self, return_value):
        self.return_value = return_value

    def __call__(self, name, trait):
        return self.return_value

    def __eq__(self, other):
        return self.return_value == other.return_value

    def __hash__(self):
        return hash(self.return_value)


def create_observer(**kwargs):
    values = dict(
        notify=True,
        filter=DummyFilter(return_value=True),
    )
    values.update(kwargs)
    return FilteredTraitObserver(**values)


class TestFilteredTraitObserverEqualHashImmutable(unittest.TestCase):
    """ Tests for FilteredTraitObserver __eq__ and __hash__ methods, and
    the fact it is not mutable.
    """

    def test_not_equal_filter(self):
        observer1 = FilteredTraitObserver(
            notify=True,
            filter=DummyFilter(return_value=True),
        )
        observer2 = FilteredTraitObserver(
            notify=True,
            filter=DummyFilter(return_value=False),
        )
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_notify(self):
        filter_func = mock.Mock()
        observer1 = FilteredTraitObserver(
            notify=False, filter=filter_func)
        observer2 = FilteredTraitObserver(
            notify=True, filter=filter_func)
        self.assertNotEqual(observer1, observer2)

    def test_equal_filter_notify(self):
        observer1 = FilteredTraitObserver(
            notify=True,
            filter=DummyFilter(return_value=True),
        )
        observer2 = FilteredTraitObserver(
            notify=True,
            filter=DummyFilter(return_value=True),
        )
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_not_equal_type(self):
        filter_func = mock.Mock()
        observer1 = FilteredTraitObserver(
            notify=True,
            filter=filter_func,
        )
        imposter = mock.Mock()
        imposter.notify = True
        imposter.filter = filter_func
        self.assertNotEqual(observer1, imposter)


class Dummy(HasTraits):

    number = Int()


class DummyParent(HasTraits):

    number = Int()

    number2 = Int()

    instance = Instance(Dummy, allow_none=True)

    instance2 = Instance(Dummy)

    income = Float()

    dummies = List(Dummy)


class TestFilteredTraitObserverIterObservables(unittest.TestCase):
    """ Test FilteredTraitObserver.iter_observables """

    def test_iter_observables_with_filter(self):
        instance = DummyParent()

        observer = create_observer(
            filter=lambda name, trait: type(trait.trait_type) is Int,
        )

        actual = list(observer.iter_observables(instance))
        expected = [
            instance._trait("number", 2),
            instance._trait("number2", 2),
        ]
        self.assertCountEqual(actual, expected)

    def test_iter_observable_error(self):
        observer = create_observer()
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_observables(None))

        self.assertIn(
            "Unable to obtain trait definitions from None",
            str(exception_context.exception)
        )


class TestFilteredTraitObserverIterObjects(unittest.TestCase):
    """ Test FilteredTraitObserver.iter_objects """

    def test_iter_objects(self):
        instance = DummyParent()
        instance.instance = Dummy()
        self.assertIsNone(instance.instance2)

        observer = create_observer(
            filter=lambda name, trait: type(trait.trait_type) is Instance,
        )

        actual = list(observer.iter_objects(instance))

        # the None value is skipped here
        self.assertEqual(actual, [instance.instance])

        # when
        instance.instance2 = Dummy()
        actual = list(observer.iter_objects(instance))

        # then
        self.assertCountEqual(
            actual,
            [instance.instance, instance.instance2]
        )

    def test_iter_objects_error(self):
        observer = create_observer()
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_objects(None))

        self.assertIn(
            "Unable to obtain trait definitions from None",
            str(exception_context.exception)
        )

# ------------------------------------
# Integration tests with notifiers
# ------------------------------------


class WatchfulObserver(DummyObserver):
    """ This is a dummy observer to be used as the next observer following
    FilteredTraitObserver.
    """
    def iter_observables(self, object):
        if object in (Undefined, Uninitialized, None):
            raise ValueError(
                "Child observer unexpectedly receive {}".format(object)
            )
        yield from self.observables


class TestFilteredTraitObserverNotifications(unittest.TestCase):
    """ Integration tests with HasTraits and notifiers."""

    def test_notify_filter_values_changed(self):
        instance = DummyParent()

        # Observes number and number2
        observer = create_observer(
            filter=lambda name, trait: type(trait.trait_type) is Int,
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance,
            graph=create_graph(observer),
            handler=handler,
        )

        # when
        instance.number += 1

        # then
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        instance.number2 += 1

        # then
        self.assertEqual(handler.call_count, 1)

    def test_notifier_can_be_removed(self):

        def filter_func(name, trait):
            return name.startswith("num")

        instance = DummyParent()
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance,
            graph=create_graph(
                create_observer(filter=filter_func)
            ),
            handler=handler,
        )

        # sanity check
        instance.number += 1
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        call_add_or_remove_notifiers(
            object=instance,
            graph=create_graph(
                create_observer(filter=filter_func)
            ),
            handler=handler,
            remove=True,
        )

        # then
        instance.number += 1
        self.assertEqual(handler.call_count, 0)

    def test_maintainer_notifier(self):
        # Test maintaining downstream notifier

        # Observes a nested instance
        observer = create_observer(
            filter=lambda name, trait: type(trait.trait_type) is Instance,
        )
        observable = DummyObservable()
        notifier = DummyNotifier()
        child_observer = WatchfulObserver(
            observables=[observable],
            notifier=notifier,
        )
        instance = DummyParent()
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance,
            graph=create_graph(
                observer,
                child_observer,
            ),
            handler=handler,
        )

        # when
        # this will trigger the maintainer
        instance.instance = Dummy()

        # then
        self.assertEqual(observable.notifiers, [notifier])

        # when
        instance.instance = None

        # then
        self.assertEqual(observable.notifiers, [])
