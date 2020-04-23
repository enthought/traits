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

from traits.observers._observe import add_or_remove_notifiers
from traits.observers._observer_graph import ObserverGraph


class DummyObservable:
    """ A dummy implementation of IObservable for testing purposes."""

    def __init__(self):
        self.notifiers = []

    def _notifiers(self, force_create):
        return self.notifiers


class DummyNotifier:
    """ A dummy implementation of INotifier for testing purposes."""

    def add_to(self, observable):
        observable._notifiers(True).append(self)

    def remove_from(self, observable):
        observable._notifiers(True).remove(self)


class DummyObserver:
    """ A dummy implementation of IObserver for testing purposes.
    """

    def __init__(
            self, notify, observables, next_objects,
            notifier, maintainer, extra_graphs):
        self.notify = notify
        self.observables = observables
        self.next_objects = next_objects
        self.notifier = notifier
        self.maintainer = maintainer
        self.extra_graphs = extra_graphs

    def __eq__(self, other):
        return other is self

    def __hash__(self):
        return 1

    def iter_observables(self, object):
        yield from self.observables

    def iter_objects(self, object):
        yield from self.next_objects

    def get_notifier(
            self, handler, target, dispatcher):
        return self.notifier

    def get_maintainer(
            self, graph, handler, target, dispatcher):
        return self.maintainer

    def iter_extra_graphs(self, graph):
        yield from self.extra_graphs


def create_observer(**kwargs):
    """ Convenient function for creating a DummyObserver.

    Parameters
    ----------
    notify : boolean
        The mocked return value from IObserver.notify
    observables : iterable of IObservable
        The mocked yielded values from IObserver.iter_observables
    next_objects : iterable of object
        The mocked yielded values from IObserver.iter_objects
    notifier : INotifier
        The mocked returned value from IObserver.get_notifier
    maintainer : INotifier
        The mocked returned value from IObserver.get_maintainer
    extra_graphs : iterable of ObserverGraph
        The mocked yielded values from IObserver.iter_extra_graphs
    """
    values = dict(
        notify=True,
        observables=[],
        next_objects=[],
        notifier=DummyNotifier(),
        maintainer=DummyNotifier(),
        extra_graphs=[],
    )
    values.update(kwargs)
    return DummyObserver(**values)


def call_add_or_remove_notifiers(**kwargs):
    """ Convenient function for calling add_or_remove_notifiers
    with some default inputs.

    Parameters
    ----------
    **kwargs
        New values to use instead of the defaults
    """
    values = dict(
        object=mock.Mock(),
        graph=ObserverGraph(node=None),
        handler=mock.Mock(),
        target=mock.Mock(),
        dispatcher=mock.Mock(),
        remove=False,
    )
    values.update(kwargs)
    add_or_remove_notifiers(**values)


class TestObserveAddNotifier(unittest.TestCase):
    """ Test the add_notifiers action."""

    def test_add_trait_notifiers(self):
        observable = DummyObservable()
        notifier = DummyNotifier()
        observer = create_observer(
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
        observer = create_observer(
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
        root_observer = create_observer(
            notify=False,
            observables=[observable],
            maintainer=maintainer,
        )
        # two children, each will have a maintainer
        graph = ObserverGraph(
            node=root_observer,
            children=[
                ObserverGraph(node=create_observer()),
                ObserverGraph(node=create_observer()),
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
        child_observer1 = create_observer(
            observables=[observable1],
        )
        observable2 = DummyObservable()
        child_observer2 = create_observer(
            observables=[observable2],
        )
        parent_observer = create_observer(
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
        extra_observer = create_observer(
            observables=[observable],
            notifier=extra_notifier,
        )
        extra_graph = ObserverGraph(
            node=extra_observer,
        )
        observer = create_observer(
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


class TestObserveRemoveNotifier(unittest.TestCase):
    """ Test the remove action."""

    def test_remove_trait_notifiers(self):
        observable = DummyObservable()
        notifier = DummyNotifier()
        observable.notifiers = [notifier]

        observer = create_observer(
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

        observer = create_observer(
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

        root_observer = create_observer(
            notify=False,
            observables=[observable],
            maintainer=maintainer,
        )

        # for there are two children graphs
        # two maintainers will be removed.
        graph = ObserverGraph(
            node=root_observer,
            children=[
                ObserverGraph(node=create_observer()),
                ObserverGraph(node=create_observer()),
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
        child_observer1 = create_observer(
            observables=[observable1],
            notifier=notifier1,
        )
        observable2 = DummyObservable()
        notifier2 = DummyNotifier()
        child_observer2 = create_observer(
            observables=[observable2],
            notifier=notifier2,
        )
        parent_observer = create_observer(
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
        extra_observer = create_observer(
            observables=[observable],
            notifier=extra_notifier,
        )
        extra_graph = ObserverGraph(
            node=extra_observer,
        )
        observer = create_observer(
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
        observer = create_observer(
            observables=[DummyObservable()],
            notifier=DummyNotifier(),
        )

        with self.assertRaises(ValueError):
            call_add_or_remove_notifiers(
                graph=ObserverGraph(node=observer),
                remove=True,
            )
