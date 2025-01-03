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

from traits.api import Bool, HasTraits, Int, Instance
from traits.observation._named_trait_observer import (
    NamedTraitObserver,
)
from traits.observation._observer_graph import ObserverGraph
from traits.observation._testing import (
    call_add_or_remove_notifiers,
    create_graph,
    DummyObserver,
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

    def test_slots(self):
        observer = NamedTraitObserver(name="foo", notify=True, optional=True)
        with self.assertRaises(AttributeError):
            observer.__dict__
        with self.assertRaises(AttributeError):
            observer.__weakref__

    def test_eval_repr_roundtrip(self):
        observer = NamedTraitObserver(name="foo", notify=True, optional=True)
        self.assertEqual(eval(repr(observer)), observer)


class TestObserverGraphIntegrateNamedTraitObserver(unittest.TestCase):
    """ Test integrating ObserverGraph with NamedTraitObserver as nodes.
    """

    def test_observer_graph_hash_with_named_listener(self):
        # Test equality + hashing using set passes.

        path1 = ObserverGraph(
            node=create_observer(name="foo"),
            children=[
                ObserverGraph(node=create_observer(name="bar")),
            ],
        )
        path2 = ObserverGraph(
            node=create_observer(name="foo"),
            children=[
                ObserverGraph(node=create_observer(name="bar")),
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

    def test_trait_not_found_skip_as_optional(self):
        observer = create_observer(name="sally", optional=True)
        foo = ClassWithInstance()
        actual = list(observer.iter_objects(foo))
        self.assertEqual(actual, [])

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

    def test_maintain_notifier_change_to_new_value(self):
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

    def test_maintain_notifier_change_to_none(self):
        # Instance may accept None, maintainer should accomodate that
        # and skip it for the next observer.

        class UnassumingObserver(DummyObserver):
            def iter_observables(self, object):
                if object is None:
                    raise ValueError("This observer cannot handle None.")
                yield from ()

        foo = ClassWithInstance()
        graph = create_graph(
            create_observer(name="instance", notify=True),
            UnassumingObserver(),
        )
        handler = mock.Mock()
        call_add_or_remove_notifiers(
            object=foo,
            graph=graph,
            handler=handler,
        )

        foo.instance = ClassWithTwoValue()

        try:
            foo.instance = None
        except Exception:
            self.fail("Setting instance back to None should not fail.")

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

    def test_get_maintainer_excuse_old_value_with_no_notifiers(self):
        # The "instance" trait has a default that has not been
        # materialized prior to the user setting a new value to the trait.
        # There isn't an old: Uninitialized -> new: Default value change event.
        # Instead, there is a old: Default -> new value event.
        # The old default value in this event won't have any notifiers
        # to be removed, therefore we need to excuse the NotifierNotFound
        # in the maintainer when it tries to remove notifiers from the old
        # value.

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

        try:
            foo.instance = ClassWithTwoValue()
        except Exception:
            self.fail(
                "Reassigning the instance value should not fail."
            )


class TestNamedTraitObserverTraitAdded(unittest.TestCase):
    """ Test integration with the trait_added event."""

    def test_observe_respond_to_trait_added(self):
        graph = create_graph(
            create_observer(name="value", notify=True, optional=True),
        )
        handler = mock.Mock()
        foo = ClassWithInstance()

        # when
        # does not complain because optional is set to true
        call_add_or_remove_notifiers(object=foo, graph=graph, handler=handler)

        # when
        foo.add_trait("value", Int())

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        foo.value += 1

        # then
        self.assertEqual(handler.call_count, 1)

    def test_observe_remove_notifiers_remove_trait_added(self):
        graph = create_graph(
            create_observer(name="value", notify=True, optional=True),
        )
        handler = mock.Mock()
        foo = ClassWithInstance()

        # when
        # The following should cancel each other
        call_add_or_remove_notifiers(
            object=foo, graph=graph, handler=handler, remove=False)
        call_add_or_remove_notifiers(
            object=foo, graph=graph, handler=handler, remove=True)

        # when
        foo.add_trait("value", Int())

        # then
        self.assertEqual(handler.call_count, 0)

        # when
        foo.value += 1

        # then
        self.assertEqual(handler.call_count, 0)

    def test_remove_notifiers_after_trait_added(self):
        graph = create_graph(
            create_observer(name="value", notify=True, optional=True),
        )
        handler = mock.Mock()
        foo = ClassWithInstance()
        call_add_or_remove_notifiers(
            object=foo, graph=graph, handler=handler, remove=False)

        # when
        foo.add_trait("value", Int())

        # sanity check
        foo.value += 1
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        call_add_or_remove_notifiers(
            object=foo, graph=graph, handler=handler, remove=True)

        # then
        foo.value += 1
        self.assertEqual(handler.call_count, 0)

    def test_remove_trait_then_add_trait_again(self):
        # Test a scenario where a trait exists when the observer is hooked,
        # but then the trait is removed, and then added back again, the
        # observer is gone, because the CTrait is gone and the trait_added
        # event is not fired for something already defined on the class.

        # given
        # the trait exists, we can set optional to false.
        graph = create_graph(
            create_observer(name="value1", notify=True, optional=False),
        )
        handler = mock.Mock()
        foo = ClassWithTwoValue()
        call_add_or_remove_notifiers(
            object=foo, graph=graph, handler=handler, remove=False)

        # sanity check, the handler is called when the trait changes.
        foo.value1 += 1
        handler.assert_called_once()
        handler.reset_mock()

        # when
        # remove the trait
        foo.remove_trait("value1")

        # then
        # the handler is gone with the instance trait.
        foo.value1 += 1
        handler.assert_not_called()

        # when
        # Add the trait back...
        foo.add_trait("value1", Int())

        # then
        # won't bring the handler back, because the 'value1' is defined as a
        # class trait, trait_added is not fired when it is added.
        foo.value1 += 1
        handler.assert_not_called()

    def test_add_trait_remove_trait_then_add_trait_again(self):
        # Test a scenario when a trait is added, then removed, then added back.

        # given
        # trait is optional. It will be added later.
        graph = create_graph(
            create_observer(name="new_value", notify=True, optional=True),
        )
        handler = mock.Mock()
        foo = ClassWithInstance()
        call_add_or_remove_notifiers(
            object=foo, graph=graph, handler=handler, remove=False)

        foo.add_trait("new_value", Int())
        foo.new_value += 1
        handler.assert_called_once()
        handler.reset_mock()

        # when
        # remove the trait and then add it back
        foo.remove_trait("new_value")
        foo.add_trait("new_value", Int())

        # then
        # the handler is now back! The trait was not defined on the class,
        # so the last 'add_trait' fires a trait_added event.
        foo.new_value += 1
        handler.assert_called_once()

    def test_notifier_trait_added_distinguished(self):
        # Add two observers, both will have their own additional trait_added
        # observer. When one is removed, the other one is not affected.
        graph1 = create_graph(
            create_observer(name="some_value1", notify=True, optional=True),
        )
        graph2 = create_graph(
            create_observer(name="some_value2", notify=True, optional=True),
        )

        handler = mock.Mock()
        foo = ClassWithInstance()
        # Add two observers
        call_add_or_remove_notifiers(
            object=foo, graph=graph1, handler=handler, remove=False)
        call_add_or_remove_notifiers(
            object=foo, graph=graph2, handler=handler, remove=False)

        # when
        # Now remove the second observer
        call_add_or_remove_notifiers(
            object=foo, graph=graph2, handler=handler, remove=True)

        # the first one should still respond to trait_added event
        foo.add_trait("some_value1", Int())
        foo.some_value1 += 1

        # then
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        # the second observer has been removed
        foo.add_trait("some_value2", Int())
        foo.some_value2 += 1

        # then
        self.assertEqual(handler.call_count, 0)

    def test_optional_trait_added(self):
        graph = create_graph(
            create_observer(name="value", notify=True, optional=True),
        )
        handler = mock.Mock()

        not_an_has_traits_instance = mock.Mock()

        # does not complain because optional is set to true
        try:
            call_add_or_remove_notifiers(
                object=not_an_has_traits_instance,
                graph=graph,
                handler=handler,
            )
        except Exception:
            self.fail("Optional flag should have been propagated.")
