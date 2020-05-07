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

from traits.api import Bool, HasTraits, Int, Instance
from traits.observers._named_trait_observer import (
    NamedTraitObserver,
)
from traits.observers._observer_graph import ObserverGraph
from traits.observers._testing import (
    call_add_or_remove_notifiers,
    create_graph,
)


def create_observer(**kwargs):
    """ Convenient function for creating an instance of NamedTraitObserver.
    """
    values = dict(
        name="name",
        notify=True,
        optional=False,
    )
    values.update(kwargs)
    return NamedTraitObserver(**values)


class TestNamedTraitObserverEqualHash(unittest.TestCase):
    """ Unit tests on the NamedTraitObserver __eq__ and __hash__ methods."""

    def test_not_equal_notify(self):
        observer1 = NamedTraitObserver(name="foo", notify=True, optional=True)
        observer2 = NamedTraitObserver(name="foo", notify=False, optional=True)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_name(self):
        observer1 = NamedTraitObserver(name="foo", notify=True, optional=True)
        observer2 = NamedTraitObserver(name="bar", notify=True, optional=True)
        self.assertNotEqual(observer1, observer2)

    def test_not_equal_optional(self):
        observer1 = NamedTraitObserver(name="foo", notify=True, optional=False)
        observer2 = NamedTraitObserver(name="foo", notify=True, optional=True)
        self.assertNotEqual(observer1, observer2)

    def test_equal_observers(self):
        observer1 = NamedTraitObserver(name="foo", notify=True, optional=True)
        observer2 = NamedTraitObserver(name="foo", notify=True, optional=True)
        self.assertEqual(observer1, observer2)
        self.assertEqual(hash(observer1), hash(observer2))

    def test_not_equal_type(self):
        observer = NamedTraitObserver(name="foo", notify=True, optional=True)
        imposter = mock.Mock()
        imposter.name = "foo"
        imposter.notify = True
        imposter.optional = True
        self.assertNotEqual(observer, imposter)

    def test_name_not_mutable(self):
        observer = NamedTraitObserver(name="foo", notify=True, optional=True)
        with self.assertRaises(AttributeError) as exception_context:
            observer.name = "bar"
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")

    def test_notify_not_mutable(self):
        observer = NamedTraitObserver(name="foo", notify=True, optional=True)
        with self.assertRaises(AttributeError) as exception_context:
            observer.notify = False
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")

    def test_optional_not_mutable(self):
        observer = NamedTraitObserver(name="foo", notify=True, optional=True)
        with self.assertRaises(AttributeError) as exception_context:
            observer.optional = False
        self.assertEqual(
            str(exception_context.exception), "can't set attribute")


class TestObserverGraphIntegrateNamedTraitObserver(unittest.TestCase):
    """ Test integrating ObserverGraph with NamedTraitObserver as nodes.
    """

    def test_observer_graph_hash_with_named_listener(self):
        # Test equality + hashing using set passes.

        path1 = ObserverGraph(
            node=create_observer(name="foo"),
            children=[
                create_observer(name="bar"),
            ],
        )
        path2 = ObserverGraph(
            node=create_observer(name="foo"),
            children=[
                create_observer(name="bar"),
            ],
        )
        # This tests __eq__ and __hash__
        self.assertEqual(path1, path2)


# -----------------------------------
# Integration tests with HasTraits
# -----------------------------------


class ClassWithTwoValue(HasTraits):
    value1 = Int()
    value2 = Int()


class ClassWithInstance(HasTraits):
    instance = Instance(ClassWithTwoValue)


class ClassWithDefault(HasTraits):

    instance = Instance(ClassWithTwoValue)

    instance_default_calculated = Bool(False)

    def _instance_default(self):
        self.instance_default_calculated = True
        return ClassWithTwoValue()


class TestNamedTraitObserverIterObservable(unittest.TestCase):
    """ Tests for NamedTraitObserver.iter_observables """

    def test_ordinary_has_traits(self):
        observer = create_observer(name="value1", optional=False)

        foo = ClassWithTwoValue()

        actual = list(observer.iter_observables(foo))
        self.assertEqual(actual, [foo._trait("value1", 2)])

    def test_trait_not_found(self):
        observer = create_observer(name="billy", optional=False)
        bar = ClassWithTwoValue()

        with self.assertRaises(ValueError) as e:
            next(observer.iter_observables(bar))

        self.assertEqual(
            str(e.exception),
            "Trait named 'billy' not found on {!r}.".format(bar))

    def test_trait_not_found_skip_as_optional(self):
        observer = create_observer(name="billy", optional=True)
        bar = ClassWithTwoValue()
        actual = list(observer.iter_observables(bar))
        self.assertEqual(actual, [])


class TestNamedTraitObserverNextObjects(unittest.TestCase):
    """ Tests for NamedTraitObserver.iter_objects for the downstream
    observers.
    """

    def test_iter_objects(self):
        observer = create_observer(name="instance")
        foo = ClassWithInstance(instance=ClassWithTwoValue())
        actual = list(observer.iter_objects(foo))
        self.assertEqual(actual, [foo.instance])

    def test_iter_objects_raises_if_trait_not_found(self):
        observer = create_observer(name="sally", optional=False)
        foo = ClassWithInstance()

        with self.assertRaises(ValueError) as e:
            next(observer.iter_objects(foo))
        self.assertEqual(
            str(e.exception),
            "Trait named {!r} not found on {!r}.".format("sally", foo)
        )

    def test_iter_objects_no_side_effect_on_default_initializer(self):
        # Test iter_objects should not trigger default to be evaluated.
        observer = create_observer(name="instance")
        foo = ClassWithDefault()

        actual = list(observer.iter_objects(foo))
        self.assertEqual(actual, [])
        self.assertNotIn("instance", foo.__dict__)
        self.assertFalse(
            foo.instance_default_calculated,
            "Unexpected side-effect on the default initializer."
        )


class TestNamedTraitObserverNotifications(unittest.TestCase):
    """ Test integration with observe and HasTraits
    to get notifications.
    """

    def test_notifier_extended_trait_change(self):

        foo = ClassWithInstance()
        graph = create_graph(
            create_observer(name="instance", notify=True),
            create_observer(name="value1", notify=True),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=foo,
            graph=graph,
            handler=handler,
        )
        self.assertIsNone(foo.instance)

        # when
        foo.instance = ClassWithTwoValue()

        # then
        ((event, ), _), = handler.call_args_list
        self.assertEqual(event.object, foo)
        self.assertEqual(event.name, "instance")
        self.assertEqual(event.old, None)
        self.assertEqual(event.new, foo.instance)

        # when
        handler.reset_mock()
        foo.instance.value1 += 1

        # then
        ((event, ), _), = handler.call_args_list
        self.assertEqual(event.object, foo.instance)
        self.assertEqual(event.name, "value1")
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 1)

    def test_maintain_notifier(self):
        # Test when the container object is changed, the notifiers are
        # maintained downstream.

        foo = ClassWithInstance()
        graph = create_graph(
            create_observer(name="instance", notify=True),
            create_observer(name="value1", notify=True),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=foo,
            graph=graph,
            handler=handler,
        )

        # sanity check
        foo.instance = ClassWithTwoValue()
        foo.instance.value1 += 1
        self.assertEqual(handler.call_count, 2)

        # when
        old_instance = foo.instance
        foo.instance = ClassWithTwoValue()
        handler.reset_mock()
        old_instance.value1 += 1

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        foo.instance.value1 += 1

        # then
        self.assertEqual(handler.call_count, 1)

    def test_maintain_notifier_for_default(self):
        # Dynamic defaults are not computed when hooking up the notifiers.
        # By when the default is defined, the maintainer will then hook up
        # the child observer.

        foo = ClassWithDefault()
        graph = create_graph(
            create_observer(name="instance", notify=True),
            create_observer(name="value1", notify=True),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=foo,
            graph=graph,
            handler=handler,
        )

        # sanity check test setup.
        self.assertNotIn("instance", foo.__dict__)

        # when
        foo.instance   # this triggers the default to be computed and set

        # then
        # setting the default does not trigger notifications
        self.assertEqual(handler.call_count, 0)

        # when
        foo.instance.value1 += 1

        # then
        # the notifier for value1 has been hooked up by the maintainer
        self.assertEqual(handler.call_count, 1)
