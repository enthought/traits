# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
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
from traits.trait_types import Instance, Int
from traits.observation.api import (
    pop_exception_handler,
    push_exception_handler,
)
from traits.observation.exceptions import NotifierNotFound
from traits.observation.expression import compile_expr, trait
from traits.observation.observe import (
    apply_observers,
    dispatch_same,
    observe,
)
from traits.observation._observer_graph import ObserverGraph
from traits.observation._testing import (
    call_add_or_remove_notifiers,
    create_graph,
    DummyNotifier,
    DummyObservable,
    DummyObserver,
)


class TestObserveAddNotifier(unittest.TestCase):
    """ Test the add_notifiers action."""

    def test_add_trait_notifiers(self):
        observable = DummyObservable()
        notifier = DummyNotifier()
        observer = DummyObserver(
            notify=True,
            observables=[observable],
            notifier=notifier,
        )
        graph = ObserverGraph(node=observer)

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=False,
        )

        # then
        self.assertEqual(observable.notifiers, [notifier])

    def test_add_trait_notifiers_notify_flag_is_false(self):
        # Test when the notify flag is false, the notifier is not
        # added.
        observable = DummyObservable()
        notifier = DummyNotifier()
        observer = DummyObserver(
            notify=False,
            observables=[observable],
            notifier=notifier,
        )
        graph = ObserverGraph(node=observer)

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=False,
        )

        # then
        self.assertEqual(observable.notifiers, [])

    def test_add_maintainers(self):
        # Test adding maintainers for children graphs
        observable = DummyObservable()
        maintainer = DummyNotifier()
        root_observer = DummyObserver(
            notify=False,
            observables=[observable],
            maintainer=maintainer,
        )
        # two children, each will have a maintainer
        graph = ObserverGraph(
            node=root_observer,
            children=[
                ObserverGraph(node=DummyObserver()),
                ObserverGraph(node=DummyObserver()),
            ],
        )

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=False,
        )

        # then
        # the dummy observer always return the same maintainer object.
        self.assertEqual(
            observable.notifiers, [maintainer, maintainer])

    def test_add_notifiers_for_children_graphs(self):
        # Test adding notifiers using children graphs
        observable1 = DummyObservable()
        child_observer1 = DummyObserver(
            observables=[observable1],
        )
        observable2 = DummyObservable()
        child_observer2 = DummyObserver(
            observables=[observable2],
        )
        parent_observer = DummyObserver(
            next_objects=[mock.Mock()],
        )
        graph = ObserverGraph(
            node=parent_observer,
            children=[
                ObserverGraph(
                    node=child_observer1,
                ),
                ObserverGraph(
                    node=child_observer2,
                )
            ],
        )

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=False,
        )

        # then
        self.assertCountEqual(
            observable1.notifiers,
            [
                # For child1 observer
                child_observer1.notifier,
            ]
        )
        self.assertCountEqual(
            observable2.notifiers,
            [
                # For child2 observer
                child_observer2.notifier,
            ]
        )

    def test_add_notifiers_for_extra_graph(self):
        observable = DummyObservable()
        extra_notifier = DummyNotifier()
        extra_observer = DummyObserver(
            observables=[observable],
            notifier=extra_notifier,
        )
        extra_graph = ObserverGraph(
            node=extra_observer,
        )
        observer = DummyObserver(
            extra_graphs=[extra_graph],
        )
        graph = ObserverGraph(node=observer)

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=False,
        )

        # then
        self.assertEqual(
            observable.notifiers, [extra_notifier]
        )

    def test_add_notifier_atomic(self):

        class BadNotifier(DummyNotifier):
            def add_to(self, observable):
                raise ZeroDivisionError()

        observable = DummyObservable()
        good_observer = DummyObserver(
            notify=True,
            observables=[observable],
            next_objects=[mock.Mock()],
            notifier=DummyNotifier(),
            maintainer=DummyNotifier(),
        )
        bad_observer = DummyObserver(
            notify=True,
            observables=[observable],
            notifier=BadNotifier(),
            maintainer=DummyNotifier(),
        )
        graph = create_graph(
            good_observer,
            bad_observer,
        )

        # when
        with self.assertRaises(ZeroDivisionError):
            call_add_or_remove_notifiers(
                object=mock.Mock(),
                graph=graph,
            )

        # then
        self.assertEqual(observable.notifiers, [])


class TestObserveRemoveNotifier(unittest.TestCase):
    """ Test the remove action."""

    def test_remove_trait_notifiers(self):
        observable = DummyObservable()
        notifier = DummyNotifier()
        observable.notifiers = [notifier]

        observer = DummyObserver(
            observables=[observable],
            notifier=notifier,
        )
        graph = ObserverGraph(
            node=observer,
        )

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=True,
        )

        # then
        self.assertEqual(observable.notifiers, [])

    def test_remove_notifiers_skip_if_notify_flag_is_false(self):
        observable = DummyObservable()
        notifier = DummyNotifier()
        observable.notifiers = [notifier]

        observer = DummyObserver(
            notify=False,
            observables=[observable],
            notifier=notifier,
        )
        graph = ObserverGraph(
            node=observer,
        )

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=True,
        )

        # then
        # notify is false, remove does nothing.
        self.assertEqual(
            observable.notifiers, [notifier]
        )

    def test_remove_maintainers(self):
        observable = DummyObservable()
        maintainer = DummyNotifier()
        observable.notifiers = [maintainer, maintainer]

        root_observer = DummyObserver(
            notify=False,
            observables=[observable],
            maintainer=maintainer,
        )

        # for there are two children graphs
        # two maintainers will be removed.
        graph = ObserverGraph(
            node=root_observer,
            children=[
                ObserverGraph(node=DummyObserver()),
                ObserverGraph(node=DummyObserver()),
            ],
        )

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=True,
        )

        # then
        self.assertEqual(observable.notifiers, [])

    def test_remove_notifiers_for_children_graphs(self):
        observable1 = DummyObservable()
        notifier1 = DummyNotifier()
        child_observer1 = DummyObserver(
            observables=[observable1],
            notifier=notifier1,
        )
        observable2 = DummyObservable()
        notifier2 = DummyNotifier()
        child_observer2 = DummyObserver(
            observables=[observable2],
            notifier=notifier2,
        )
        parent_observer = DummyObserver(
            next_objects=[mock.Mock()],
        )

        graph = ObserverGraph(
            node=parent_observer,
            children=[
                ObserverGraph(
                    node=child_observer1,
                ),
                ObserverGraph(
                    node=child_observer2,
                )
            ],
        )

        # suppose notifiers were added
        observable1.notifiers = [notifier1]
        observable2.notifiers = [notifier2]

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=True,
        )

        # then
        self.assertEqual(observable1.notifiers, [])
        self.assertEqual(observable2.notifiers, [])

    def test_remove_notifiers_for_extra_graph(self):
        observable = DummyObservable()
        extra_notifier = DummyNotifier()
        extra_observer = DummyObserver(
            observables=[observable],
            notifier=extra_notifier,
        )
        extra_graph = ObserverGraph(
            node=extra_observer,
        )
        observer = DummyObserver(
            extra_graphs=[extra_graph],
        )
        graph = ObserverGraph(node=observer)

        # suppose the notifier was added before
        observable.notifiers = [extra_notifier]

        # when
        call_add_or_remove_notifiers(
            graph=graph,
            remove=True,
        )

        # then
        self.assertEqual(observable.notifiers, [])

    def test_remove_notifier_raises_let_error_propagate(self):
        # Test if the notifier remove_from raises, the error will
        # be propagated.

        # DummyNotifier.remove_from raises if the notifier is not found.
        observer = DummyObserver(
            observables=[DummyObservable()],
            notifier=DummyNotifier(),
        )

        with self.assertRaises(NotifierNotFound):
            call_add_or_remove_notifiers(
                graph=ObserverGraph(node=observer),
                remove=True,
            )

    def test_remove_atomic(self):
        # Test atomicity
        notifier = DummyNotifier()
        maintainer = DummyNotifier()
        observable1 = DummyObservable()
        observable1.notifiers = [
            notifier,
            maintainer,
        ]
        old_observable1_notifiers = observable1.notifiers.copy()
        observable2 = DummyObservable()
        observable2.notifiers = [maintainer]
        old_observable2_notifiers = observable2.notifiers.copy()
        observable3 = DummyObservable()
        observable3.notifiers = [
            notifier,
            maintainer,
        ]
        old_observable3_notifiers = observable3.notifiers.copy()

        observer = DummyObserver(
            notify=True,
            observables=[
                observable1,
                observable2,
                observable3,
            ],
            notifier=notifier,
            maintainer=maintainer,
        )
        graph = create_graph(
            observer,
            DummyObserver(),  # Need a child graph to get maintainer in
        )

        # when
        with self.assertRaises(NotifierNotFound):
            call_add_or_remove_notifiers(
                object=mock.Mock(),
                graph=graph,
                remove=True,
            )

        # then
        # as if nothing has happened, the order might not be maintained though!
        self.assertCountEqual(
            observable1.notifiers,
            old_observable1_notifiers,
        )
        self.assertCountEqual(
            observable2.notifiers,
            old_observable2_notifiers,
        )
        self.assertCountEqual(
            observable3.notifiers,
            old_observable3_notifiers,
        )


# ---- Tests for public facing `observe` --------------------------------------

class ClassWithNumber(HasTraits):

    number = Int()


class ClassWithInstance(HasTraits):

    instance = Instance(ClassWithNumber)


class TestObserverIntegration(unittest.TestCase):
    """ Test the public facing observe function."""

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_observe_with_expression(self):
        foo = ClassWithNumber()
        handler = mock.Mock()

        observe(
            object=foo,
            expression=trait("number"),
            handler=handler,
        )

        # when
        foo.number += 1

        # then
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        observe(
            object=foo,
            expression=trait("number"),
            handler=handler,
            remove=True,
        )
        foo.number += 1

        # then
        self.assertEqual(handler.call_count, 0)

    def test_observe_different_dispatcher(self):

        self.dispatch_records = []

        def dispatcher(handler, event):
            self.dispatch_records.append((handler, event))

        foo = ClassWithNumber()
        handler = mock.Mock()

        # when
        observe(
            object=foo,
            expression=trait("number"),
            handler=handler,
            dispatcher=dispatcher,
        )
        foo.number += 1

        # then
        # the dispatcher is called.
        self.assertEqual(len(self.dispatch_records), 1)

    def test_observe_different_target(self):
        # Test the result of setting target to be the same as object
        parent1 = ClassWithInstance()
        parent2 = ClassWithInstance()

        # the instance is shared
        instance = ClassWithNumber()
        parent1.instance = instance
        parent2.instance = instance

        handler = mock.Mock()

        # when
        observe(
            object=parent1,
            expression=trait("instance").trait("number"),
            handler=handler,
        )
        observe(
            object=parent2,
            expression=trait("instance").trait("number"),
            handler=handler,
        )
        instance.number += 1

        # then
        # the handler should be called twice as the targets are different.
        self.assertEqual(handler.call_count, 2)

    def test_observe_with_any_callables_accepting_one_argument(self):
        # If it is a callable that works with one positional argument, it
        # can be used.

        def handler_with_one_pos_arg(arg, *, optional=None):
            pass

        callables = [
            repr,
            lambda e: False,
            handler_with_one_pos_arg,
        ]
        for callable_ in callables:
            with self.subTest(callable=callable_):
                instance = ClassWithNumber()
                instance.observe(callable_, "number")
                instance.number += 1


class TestApplyObservers(unittest.TestCase):
    """ Test the public-facing apply_observers function."""

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_apply_observers_with_expression(self):
        foo = ClassWithNumber()
        handler = mock.Mock()
        graphs = compile_expr(trait("number"))

        apply_observers(
            object=foo,
            graphs=graphs,
            handler=handler,
            dispatcher=dispatch_same,
        )

        # when
        foo.number += 1

        # then
        self.assertEqual(handler.call_count, 1)
        handler.reset_mock()

        # when
        apply_observers(
            object=foo,
            graphs=graphs,
            handler=handler,
            dispatcher=dispatch_same,
            remove=True,
        )
        foo.number += 1

        # then
        self.assertEqual(handler.call_count, 0)

    def test_apply_observers_different_dispatcher(self):

        self.dispatch_records = []

        def dispatcher(handler, event):
            self.dispatch_records.append((handler, event))

        foo = ClassWithNumber()
        handler = mock.Mock()

        # when
        apply_observers(
            object=foo,
            graphs=compile_expr(trait("number")),
            handler=handler,
            dispatcher=dispatcher,
        )
        foo.number += 1

        # then
        # the dispatcher is called.
        self.assertEqual(len(self.dispatch_records), 1)

    def test_apply_observers_different_target(self):
        # Test the result of setting target to be the same as object
        parent1 = ClassWithInstance()
        parent2 = ClassWithInstance()
        graphs = compile_expr(trait("instance").trait("number"))

        # the instance is shared
        instance = ClassWithNumber()
        parent1.instance = instance
        parent2.instance = instance

        handler = mock.Mock()

        # when
        apply_observers(
            object=parent1,
            graphs=graphs,
            handler=handler,
            dispatcher=dispatch_same,
        )
        apply_observers(
            object=parent2,
            graphs=graphs,
            handler=handler,
            dispatcher=dispatch_same,
        )
        instance.number += 1

        # then
        # the handler should be called twice as the targets are different.
        self.assertEqual(handler.call_count, 2)
