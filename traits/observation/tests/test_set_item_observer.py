# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
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
from traits.observation._set_item_observer import SetItemObserver
from traits.observation._testing import (
    call_add_or_remove_notifiers,
    create_graph,
    DummyObservable,
    DummyObserver,
    DummyNotifier,
)
from traits.trait_set_object import TraitSet
from traits.trait_types import Set


def create_observer(**kwargs):
    """ Convenience function for creating SetItemObserver with default values.
    """
    values = dict(
        notify=True,
        optional=False,
    )
    values.update(kwargs)
    return SetItemObserver(**values)


class TestSetItemObserverEqualHash(unittest.TestCase):
    """ Test SetItemObserver __eq__, __hash__ and immutability. """

    def test_not_equal_notify(self):
        observer1 = SetItemObserver(notify=False, optional=False)
        observer2 = SetItemObserver(notify=True, optional=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_optional(self):
        observer1 = SetItemObserver(notify=True, optional=True)
        observer2 = SetItemObserver(notify=True, optional=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_different_type(self):
        observer1 = SetItemObserver(notify=False, optional=False)
        imposter = mock.Mock()
        imposter.notify = False
        imposter.optional = False
        self.assertNotEqual(observer1, imposter)

    def test_equal_observers(self):
        observer1 = SetItemObserver(notify=False, optional=False)
        observer2 = SetItemObserver(notify=False, optional=False)
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_slots(self):
        observer = SetItemObserver(notify=True, optional=False)
        with self.assertRaises(AttributeError):
            observer.__dict__
        with self.assertRaises(AttributeError):
            observer.__weakref__

    def test_eval_repr_roundtrip(self):
        observer = SetItemObserver(notify=True, optional=False)
        self.assertEqual(eval(repr(observer)), observer)


class CustomSet(set):
    # This is a set, but not an observable
    pass


class CustomTraitSet(TraitSet):
    # This can be used with SetItemObserver
    pass


class ClassWithSet(HasTraits):
    values = Set()


class TestSetItemObserverIterObservable(unittest.TestCase):
    """ Test SetItemObserver.iter_observables """

    def test_trait_set_iter_observables(self):
        instance = ClassWithSet()
        observer = create_observer(optional=False)
        actual_item, = list(observer.iter_observables(instance.values))

        self.assertIs(actual_item, instance.values)

    def test_set_but_not_a_trait_set(self):
        observer = create_observer(optional=False)
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_observables(CustomSet()))

        self.assertIn(
            "Expected a TraitSet to be observed, got",
            str(exception_context.exception)
        )

    def test_iter_observables_custom_trait_set(self):
        # A subcalss of TraitSet can also be used.
        custom_trait_set = CustomTraitSet()
        observer = create_observer()

        actual_item, = list(observer.iter_observables(custom_trait_set))

        self.assertIs(actual_item, custom_trait_set)

    def test_not_a_set(self):
        observer = create_observer(optional=False)
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_observables(None))

        self.assertIn(
            "Expected a TraitSet to be observed, got",
            str(exception_context.exception)
        )

    def test_optional_flag_not_a_set(self):
        observer = create_observer(optional=True)
        actual = list(observer.iter_observables(None))
        self.assertEqual(actual, [])

    def test_optional_flag_not_an_observable(self):
        observer = create_observer(optional=True)
        actual = list(observer.iter_observables(CustomSet()))
        self.assertEqual(actual, [])


class TestSetItemObserverIterObjects(unittest.TestCase):
    """ Test SetItemObserver.iter_objects """

    def test_iter_objects_from_set(self):
        instance = ClassWithSet()
        instance.values = set([1, 2, 3])
        observer = create_observer()
        actual = list(observer.iter_objects(instance.values))
        self.assertCountEqual(actual, [1, 2, 3])

    def test_iter_observables_custom_trait_set(self):
        # A subcalss of TraitSet can also be used.
        custom_trait_set = CustomTraitSet([1, 2, 3])
        observer = create_observer()

        actual = list(observer.iter_objects(custom_trait_set))
        self.assertCountEqual(actual, [1, 2, 3])

    def test_iter_objects_sanity_check(self):
        # sanity check if the given object is a set
        observer = create_observer(optional=False)
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_objects(None))

        self.assertIn(
            "Expected a TraitSet to be observed, got",
            str(exception_context.exception),
        )

    def test_iter_objects_optional(self):
        observer = create_observer(optional=True)
        actual = list(observer.iter_objects(None))
        self.assertEqual(actual, [])


class TestSetItemObserverNotifications(unittest.TestCase):
    """ Integration tests with notifiers and HasTraits. """

    def test_notify_set_change(self):
        instance = ClassWithSet(values=set())
        graph = create_graph(
            create_observer(notify=True),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.values,
            graph=graph,
            handler=handler,
        )

        # when
        instance.values.add(1)

        # then
        ((event, ), _), = handler.call_args_list
        self.assertEqual(event.added, set([1]))
        self.assertEqual(event.removed, set())

    def test_maintain_notifier(self):
        # Test maintaining downstream notifier

        class ChildObserver(DummyObserver):

            def iter_observables(self, object):
                yield object

        instance = ClassWithSet()
        instance.values = set()

        notifier = DummyNotifier()
        child_observer = ChildObserver(notifier=notifier)
        graph = create_graph(
            create_observer(notify=False, optional=False),
            child_observer,
        )

        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.values,
            graph=graph,
            handler=handler,
        )

        # when
        observable = DummyObservable()
        instance.values.add(observable)

        # then
        self.assertEqual(observable.notifiers, [notifier])

        # when
        instance.values.remove(observable)

        # then
        self.assertEqual(observable.notifiers, [])
