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
from traits.observers._dict_item_observer import DictItemObserver
from traits.observers._testing import (
    call_add_or_remove_notifiers,
    create_graph,
    DummyObservable,
    DummyObserver,
    DummyNotifier,
)
from traits.trait_dict_object import TraitDict
from traits.trait_types import Dict


def create_observer(**kwargs):
    """ Convenient function for creating DictItemObserver with default values.
    """
    values = dict(
        notify=True,
        optional=False,
    )
    values.update(kwargs)
    return DictItemObserver(**values)


class TestDictItemObserverEqualHash(unittest.TestCase):
    """ Test DictItemObserver __eq__, __hash__ and immutability. """

    def test_not_equal_notify(self):
        observer1 = DictItemObserver(notify=False, optional=False)
        observer2 = DictItemObserver(notify=True, optional=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_optional(self):
        observer1 = DictItemObserver(notify=True, optional=True)
        observer2 = DictItemObserver(notify=True, optional=False)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_different_type(self):
        observer1 = DictItemObserver(notify=False, optional=False)
        imposter = mock.Mock()
        imposter.notify = False
        self.assertNotEqual(observer1, imposter)

    def test_equal_observers(self):
        observer1 = DictItemObserver(notify=False, optional=False)
        observer2 = DictItemObserver(notify=False, optional=False)
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_notify_not_mutable(self):
        observer = DictItemObserver(notify=True, optional=False)
        with self.assertRaises(AttributeError) as exception_context:
            observer.notify = False
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")

    def test_optional_not_mutable(self):
        observer = DictItemObserver(notify=True, optional=False)
        with self.assertRaises(AttributeError) as exception_context:
            observer.optional = False
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")


class CustomDict(dict):
    # This is a dict, but not an observable
    pass


class CustomTraitDict(TraitDict):
    # This can be observed using DictItemObserver
    pass


class ClassWithDict(HasTraits):
    values = Dict()


class TestDictItemObserverIterObservable(unittest.TestCase):
    """ Test DictItemObserver.iter_observables """

    def test_trait_dict_iter_observables(self):
        instance = ClassWithDict()
        observer = create_observer(optional=False)
        actual_item, = list(observer.iter_observables(instance.values))

        self.assertIs(actual_item, instance.values)

    def test_dict_but_not_a_trait_dict(self):
        observer = create_observer(optional=False)
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_observables(CustomDict()))

        self.assertIn(
            "Expected a TraitDict to be observed, got",
            str(exception_context.exception)
        )

    def test_custom_trait_dict_is_observable(self):
        observer = create_observer(optional=False)
        custom_trait_dict = CustomTraitDict()
        actual_item, = list(observer.iter_observables(custom_trait_dict))
        self.assertIs(actual_item, custom_trait_dict)

    def test_not_a_dict(self):
        observer = create_observer(optional=False)
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_observables(None))

        self.assertIn(
            "Expected a TraitDict to be observed, got",
            str(exception_context.exception)
        )

    def test_optional_flag_not_a_dict(self):
        observer = create_observer(optional=True)
        actual = list(observer.iter_observables(None))
        self.assertEqual(actual, [])

    def test_optional_flag_not_an_observable(self):
        observer = create_observer(optional=True)
        actual = list(observer.iter_observables(CustomDict()))
        self.assertEqual(actual, [])


class TestDictItemObserverIterObjects(unittest.TestCase):
    """ Test DictItemObserver.iter_objects """

    def test_iter_objects_from_dict(self):
        instance = ClassWithDict()
        instance.values = {"1": 1, "2": 2}
        observer = create_observer()
        actual = list(observer.iter_objects(instance.values))
        self.assertCountEqual(actual, [1, 2])

    def test_iter_objects_from_custom_trait_dict(self):
        observer = create_observer(optional=False)
        custom_trait_dict = CustomTraitDict({"1": 1, "2": 2})
        actual = list(observer.iter_objects(custom_trait_dict))
        self.assertCountEqual(actual, [1, 2])

    def test_iter_objects_sanity_check(self):
        # sanity check if the given object is a dict
        observer = create_observer(optional=False)
        with self.assertRaises(ValueError) as exception_context:
            list(observer.iter_objects(None))

        self.assertIn(
            "Expected a TraitDict to be observed",
            str(exception_context.exception),
        )

    def test_iter_objects_optional(self):
        observer = create_observer(optional=True)
        actual = list(observer.iter_objects(None))
        self.assertEqual(actual, [])


class TestDictItemObserverNotifications(unittest.TestCase):
    """ Integration tests with notifiers (including maintainers). """

    def test_notify_dict_change(self):
        instance = ClassWithDict(values=dict())
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
        instance.values.update({"1": 1})

        # then
        ((event, ), _), = handler.call_args_list
        self.assertEqual(event.added, {"1": 1})
        self.assertEqual(event.removed, {})

    def test_notify_custom_trait_dict_change(self):
        # Test using DictItemObserver for changes on a subclass of TraitDict
        # that isn't TraitDictObject
        instance = ClassWithDict(custom_trait_dict=CustomTraitDict())
        graph = create_graph(
            create_observer(notify=True),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=instance.custom_trait_dict,
            graph=graph,
            handler=handler,
        )

        # when
        instance.custom_trait_dict.update({"1": 1})

        # then
        ((event, ), _), = handler.call_args_list
        self.assertEqual(event.added, {"1": 1})
        self.assertEqual(event.removed, {})

    def test_maintain_notifier(self):
        # Test maintaining downstream notifier

        class ChildObserver(DummyObserver):

            def iter_observables(self, object):
                yield object

        instance = ClassWithDict()

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
        instance.values.update({"1": observable})

        # then
        self.assertEqual(observable.notifiers, [notifier])

        # when
        del instance.values["1"]

        # then
        self.assertEqual(observable.notifiers, [])
