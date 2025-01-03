# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
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

from traits.api import HasTraits, Instance, Int, List

from traits.observation._list_item_observer import ListItemObserver
from traits.observation._testing import (
    call_add_or_remove_notifiers,
    create_graph,
)
from traits.trait_list_object import TraitList, TraitListObject


class TestListItemObserverEqualHash(unittest.TestCase):

    def test_not_equal_notify(self):
        observer1 = ListItemObserver(notify=False, optional=False)
        observer2 = ListItemObserver(notify=True, optional=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_optional(self):
        observer1 = ListItemObserver(notify=True, optional=True)
        observer2 = ListItemObserver(notify=True, optional=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_different_type(self):
        observer1 = ListItemObserver(notify=False, optional=False)
        imposter = mock.Mock()
        imposter.notify = False
        imposter.optional = False
        self.assertNotEqual(observer1, imposter)

    def test_equal_observers(self):
        observer1 = ListItemObserver(notify=False, optional=False)
        observer2 = ListItemObserver(notify=False, optional=False)
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_slots(self):
        observer = ListItemObserver(notify=True, optional=False)
        with self.assertRaises(AttributeError):
            observer.__dict__
        with self.assertRaises(AttributeError):
            observer.__weakref__

    def test_eval_repr_roundtrip(self):
        observer = ListItemObserver(notify=True, optional=False)
        self.assertEqual(eval(repr(observer)), observer)


class CustomList(list):
    pass


class CustomTraitList(TraitList):
    pass


class ClassWithList(HasTraits):

    values = List()

    not_a_trait_list = Instance(CustomList)

    number = Int()

    custom_trait_list = Instance(CustomTraitList)


class ClassWithListOfList(HasTraits):

    list_of_list = List(List())


class TestListItemObserverIterObservable(unittest.TestCase):
    """ Test ListItemObserver.iter_observables """

    def test_trait_list_iter_observables(self):
        instance = ClassWithList()
        instance.values = [1, 2, 3]

        observer = ListItemObserver(notify=True, optional=False)

        # In the expected scenario, the ListItemObserver will
        # follow another observer whose iter_objects will yield
        # the trait value
        actual_item, = list(observer.iter_observables(instance.values))
        self.assertIs(actual_item, instance.values)

    def test_trait_list_iter_observables_with_default_list(self):
        instance = ClassWithList()

        observer = ListItemObserver(notify=True, optional=False)

        # In the expected scenario, the ListItemObserver will
        # follow another observer whose iter_objects will yield
        # the trait value
        actual_item, = list(observer.iter_observables(instance.values))
        self.assertIsInstance(actual_item, TraitListObject)

    def test_trait_list_iter_observables_accept_custom_trait_list(self):
        # An extension of TraitList can be used with ListItemObserver
        instance = ClassWithList()
        instance.custom_trait_list = CustomTraitList([1, 2, 3])

        observer = ListItemObserver(notify=True, optional=False)

        actual_item, = list(
            observer.iter_observables(instance.custom_trait_list))
        self.assertIs(actual_item, instance.custom_trait_list)

    def test_trait_list_iter_observables_error(self):
        # If the user chains a ListItemObserver after an observer that
        # does not produce a TraitList, raise an error

        instance = ClassWithList()
        instance.not_a_trait_list = CustomList()
        observer = ListItemObserver(notify=True, optional=False)

        with self.assertRaises(ValueError) as exception_context:
            next(observer.iter_observables(instance.not_a_trait_list))

        self.assertIn(
            "Expected a TraitList to be observed",
            str(exception_context.exception)
        )

    def test_trait_list_iter_observables_not_a_trait_list_optional(self):
        # Test when the given object is a list but not an IObservable
        instance = ClassWithList()

        observer = ListItemObserver(notify=True, optional=True)

        self.assertIsNone(instance.not_a_trait_list)
        actual = list(observer.iter_observables(instance.not_a_trait_list))
        self.assertEqual(actual, [])

        instance.not_a_trait_list = CustomList()
        actual = list(observer.iter_observables(instance.not_a_trait_list))
        self.assertEqual(actual, [])

    def test_trait_list_iter_observables_not_a_list_error(self):
        # Test when the given object is not a list
        instance = ClassWithList()

        observer = ListItemObserver(notify=True, optional=False)

        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_observables(instance.number))

        self.assertIn(
            "Expected a TraitList to be observed",
            str(exception_context.exception))


class TestListItemObserverIterObjects(unittest.TestCase):
    """ Test ListItemObserver.iter_objects """

    def test_trait_list_iter_objects(self):
        instance = ClassWithList()
        item1 = mock.Mock()
        item2 = mock.Mock()
        instance.values = [item1, item2]

        observer = ListItemObserver(notify=True, optional=False)

        # the observer does not filter if the values are observables or not.
        actual = list(observer.iter_objects(instance.values))
        self.assertEqual(actual, [item1, item2])

    def test_trait_list_iter_object_accept_custom_trait_list(self):
        # An extension of TraitList can be used with ListItemObserver
        instance = ClassWithList()
        instance.custom_trait_list = CustomTraitList([1, 2, 3])

        observer = ListItemObserver(notify=True, optional=False)

        actual = list(
            observer.iter_objects(instance.custom_trait_list))
        self.assertEqual(actual, [1, 2, 3])

    def test_trait_list_iter_objects_complain_not_list(self):

        observer = ListItemObserver(notify=True, optional=False)
        with self.assertRaises(ValueError) as exception_cm:
            next(observer.iter_objects(set([1])))

        self.assertIn(
            "Expected a TraitList to be observed", str(exception_cm.exception))

    def test_trait_list_iter_objects_ignore_if_optional_and_not_list(self):
        observer = ListItemObserver(notify=True, optional=True)
        actual = list(observer.iter_objects(set([1])))
        self.assertEqual(actual, [])


# ----------------------------------
# Integration tests with notifiers
# ----------------------------------


class TestListTraitObserverNotifications(unittest.TestCase):

    def test_notifier_list_change(self):

        instance = ClassWithList(values=[])
        graph = create_graph(
            ListItemObserver(notify=True, optional=False),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.values,
            graph=graph,
            handler=handler,
        )

        # when
        instance.values.append(1)

        # then
        ((event, ), _), = handler.call_args_list
        self.assertIs(event.object, instance.values)
        self.assertEqual(event.added, [1])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 0)

    def test_notifier_custom_trait_list_change(self):
        # Test compatibility with any extension of TraitList, not just
        # TraitListObject
        instance = ClassWithList()
        instance.custom_trait_list = CustomTraitList()
        graph = create_graph(
            ListItemObserver(notify=True, optional=False),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.custom_trait_list,
            graph=graph,
            handler=handler,
        )

        # when
        instance.custom_trait_list.append(1)

        # then
        ((event, ), _), = handler.call_args_list
        self.assertIs(event.object, instance.custom_trait_list)
        self.assertEqual(event.added, [1])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 0)

    def test_maintain_notifier(self):
        # Test maintaining downstream notifier by
        # observing list of list

        instance = ClassWithListOfList()

        graph = create_graph(
            ListItemObserver(notify=False, optional=False),
            ListItemObserver(notify=True, optional=False),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.list_of_list,
            graph=graph,
            handler=handler,
        )

        # when
        instance.list_of_list.append([])

        # then
        # the first ListItemObserver has notify=False
        self.assertEqual(handler.call_count, 0)

        # but the second ListItemObserver is given to the nested list
        nested_list = instance.list_of_list[0]

        # when
        nested_list.append(1)

        # then
        ((event, ), _), = handler.call_args_list
        self.assertIs(event.object, nested_list)
        self.assertEqual(event.added, [1])
        self.assertEqual(event.removed, [])
        self.assertEqual(event.index, 0)
        handler.reset_mock()

        # when
        # the list is removed, it is not observed
        instance.list_of_list.pop()
        nested_list.append(1)

        # then
        self.assertEqual(handler.call_count, 0)

    def test_optional_observers(self):
        # ListItemObserver.optional is true, meaning it will ignore
        # incompatible incoming object.
        instance = ClassWithList()

        graph = create_graph(
            ListItemObserver(notify=True, optional=True),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.not_a_trait_list,
            graph=graph,
            handler=handler,
        )

        instance.not_a_trait_list = CustomList()
        instance.not_a_trait_list.append(1)

        self.assertEqual(handler.call_count, 0)
