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

from traits.api import (
    Bool, Dict, HasTraits, List, Instance, Int, Property, Set,
)
from traits.observers import _has_traits_helpers as helpers
from traits.observers.events._trait_observer_event import TraitObserverEvent
from traits.observers._testing import (
    create_graph,
    DummyObserver,
    DummyNotifier,
)
from traits.trait_base import Uninitialized


def default_dispatcher(handler, event):
    handler(event)


class Bar(HasTraits):

    count = Int()


class Foo(HasTraits):

    list_of_int = List(Int)

    instance = Instance(Bar)

    int_with_default = Int()

    int_with_default_computed = Bool()

    def _int_with_default(self):
        self.int_with_default_computed = True
        return 10

    property_value = Property()

    property_n_calculations = Int()

    def _get_property_value(self):
        self.property_n_calculations += 1
        return 1


class TestHasTraitsHelpersHasNamedTrait(unittest.TestCase):
    """ Test object_has_named_trait."""

    def test_object_has_named_trait_false_for_trait_list(self):
        foo = Foo()

        # TraitListObject that has `trait` attribute
        self.assertFalse(
            helpers.object_has_named_trait(foo.list_of_int, "bar"),
            "Expected object_has_named_trait to return false for {!r}".format(
                type(foo.list_of_int)
            )
        )

    def test_object_has_named_trait_true_basic(self):
        foo = Foo()
        self.assertTrue(
            helpers.object_has_named_trait(foo, "list_of_int"),
            "The named trait should exist."
        )

    def test_object_has_named_trait_false(self):
        foo = Foo()
        self.assertFalse(
            helpers.object_has_named_trait(foo, "not_existing"),
            "Expected object_has_named_trait to return False for a"
            "nonexisting trait name."
        )

    def test_object_has_named_trait_does_not_trigger_property(self):
        foo = Foo()
        helpers.object_has_named_trait(foo, "property_value")
        self.assertEqual(
            foo.property_n_calculations, 0
        )


class TestHasTraitsHelpersIterObjects(unittest.TestCase):
    """ Test iter_objects."""

    def test_iter_objects_avoid_undefined(self):
        foo = Foo()
        # sanity check
        self.assertNotIn("instance", foo.__dict__)

        actual = list(helpers.iter_objects(foo, "instance"))
        self.assertEqual(actual, [])

    def test_iter_objects_no_sideeffect(self):
        foo = Foo()
        # sanity check
        self.assertNotIn("instance", foo.__dict__)

        list(helpers.iter_objects(foo, "instance"))

        self.assertNotIn("instance", foo.__dict__)

    def test_iter_objects_avoid_none(self):
        foo = Foo()
        foo.instance = None

        actual = list(helpers.iter_objects(foo, "instance"))
        self.assertEqual(actual, [])

    def test_iter_objects_accepted_values(self):
        foo = Foo(instance=Bar(), list_of_int=[1, 2])
        actual = list(helpers.iter_objects(foo, "instance"))

        self.assertEqual(actual, [foo.instance])

    def test_iter_objects_does_not_evaluate_default(self):
        foo = Foo()
        list(helpers.iter_objects(foo, "int_with_default"))
        self.assertFalse(
            foo.int_with_default_computed,
            "Expect the default not to have been computed."
        )

    def test_iter_objects_does_not_trigger_property(self):
        foo = Foo()
        list(helpers.iter_objects(foo, "property_value"))
        self.assertEqual(foo.property_n_calculations, 0)


class TestHasTraitsHelpersGetNotifier(unittest.TestCase):
    """ Test get_notifier. """

    def setUp(self):
        # holding strong references to handler and target.
        self.handler = mock.Mock()
        self.target = mock.Mock()

        self.notifier = helpers.get_notifier(
            handler=self.handler,
            target=self.target,
            dispatcher=default_dispatcher,
        )

    def test_get_notifier_good_change(self):
        # when
        bar = Bar()
        self.notifier(
            object=bar, name="value", old=0, new=1,
        )

        # then
        self.assertEqual(self.handler.call_count, 1)
        ((event, ), _), = self.handler.call_args_list
        self.assertIsInstance(event, TraitObserverEvent)
        self.assertIs(event.object, bar)
        self.assertEqual(event.name, "value")
        self.assertEqual(event.old, 0)
        self.assertEqual(event.new, 1)

    def test_get_notifier_old_uninitialized(self):
        # when
        self.notifier(
            object=Bar(), name="value", old=Uninitialized, new=1,
        )

        # then
        # the event is silenced.
        self.assertEqual(self.handler.call_count, 0)


class TestHasTraitsHelpersGetMaintainer(unittest.TestCase):
    """ Test get_maintainer. """

    def setUp(self):
        # holding strong references to handler and target.
        self.handler = mock.Mock()
        self.target = mock.Mock()

    def test_get_maintainer_changed_to_new_instance(self):
        # Test the logic exercised by the maintainer.

        class BarObserver(DummyObserver):
            """ An observer specialized in observing Bar.value """

            def iter_observables(self, object):
                yield object._trait("value", 2)

            def iter_objects(self, object):
                raise NotImplementedError("Not used in this test.")

        notifier = DummyNotifier()
        bar_observer = BarObserver(notifier=notifier)

        maintainer = helpers.get_maintainer(
            graph=create_graph(bar_observer),
            handler=self.handler,
            target=self.target,
            dispatcher=default_dispatcher,
        )

        # when
        foo = Foo()
        bar1 = Bar()
        maintainer(
            object=foo, name="instance", old=Uninitialized, new=bar1,
        )

        # then
        self.assertEqual(
            bar1._trait("value", 2)._notifiers(True),
            [notifier],
        )

        # when
        bar2 = Bar()
        maintainer(
            object=foo, name="instance", old=bar1, new=bar2,
        )
        # then
        self.assertEqual(
            bar1._trait("value", 2)._notifiers(True),
            [],
        )
        self.assertEqual(
            bar2._trait("value", 2)._notifiers(True),
            [notifier],
        )

    def test_get_maintainer_changed_to_none(self):
        # Instance may accept None, maintainer should accommodate that.

        class UnassumingObserver(DummyObserver):
            def iter_observables(self, object):
                if object is None:
                    raise ValueError("This observer cannot handle None.")
                yield from ()

            def iter_objects(self, object):
                raise NotImplementedError("Not used in this test.")

        maintainer = helpers.get_maintainer(
            graph=create_graph(UnassumingObserver()),
            handler=self.handler,
            target=self.target,
            dispatcher=default_dispatcher,
        )

        try:
            maintainer(object=mock.Mock(), name="any", old=None, new=None)
        except Exception:
            self.fail("Maintainer should not fail when new value is None.")

    def test_get_maintainer_excuse_old_value_with_no_notifiers(self):
        # If the trait is referring to a TraitListObject (or friends),
        # traits may provide a default empty container as the "old" value
        # if it had not been initialized at the time of change.
        # That default empty container has no notifiers so
        # attempt to remove notifiers will fail, and we need to excuse that.

        class Observer(DummyObserver):
            def iter_observables(self, object):
                yield object

        foo = Foo()
        maintainer = helpers.get_maintainer(
            graph=create_graph(Observer()),
            handler=self.handler,
            target=self.target,
            dispatcher=default_dispatcher,
        )
        ctrait = foo._trait("list_of_int", 2)
        ctrait._notifiers(True).append(maintainer)

        try:
            foo.list_of_int = [1, 2, 3]
        except Exception:
            self.fail(
                "Reassigning a list from an otherwise uninitialized value "
                "should not faill."
            )
