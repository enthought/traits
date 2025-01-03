# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from unittest import mock

from traits.observation._observe import add_or_remove_notifiers
from traits.observation._observer_graph import ObserverGraph
from traits.observation.exceptions import NotifierNotFound


#: An object that does not get garbage collected until the very end
_DEFAULT_TARGET = mock.Mock()


def dispatch_same(handler, event):
    handler(event)


def create_graph(*nodes):
    """ Create an ObserverGraph with the given nodes joined one after another.

    Parameters
    ----------
    *nodes : hashable
        Items to be attached as nodes

    Returns
    -------
    ObserverGraph
    """
    node = nodes[-1]
    graph = ObserverGraph(node=node)
    for node in nodes[:-1][::-1]:
        graph = ObserverGraph(node=node, children=[graph])
    return graph


def call_add_or_remove_notifiers(**kwargs):
    """ Convenience function for calling add_or_remove_notifiers with default
    values.

    Parameters
    ----------
    **kwargs
        New argument values to use instead.
    """
    values = dict(
        object=mock.Mock(),
        graph=ObserverGraph(node=None),
        handler=mock.Mock(),
        target=_DEFAULT_TARGET,
        dispatcher=dispatch_same,
        remove=False,
    )
    values.update(kwargs)
    add_or_remove_notifiers(**values)


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
        notifiers = observable._notifiers(True)
        try:
            notifiers.remove(self)
        except ValueError:
            raise NotifierNotFound("Notifier not found.")


class DummyObserver:
    """ A dummy implementation of IObserver for testing purposes.

    Parameters
    ----------
    notify : boolean, optional
        The mocked return value from IObserver.notify
    observables : iterable of IObservable, optional
        The mocked yielded values from IObserver.iter_observables
    next_objects : iterable of object, optional
        The mocked yielded values from IObserver.iter_objects
    notifier : INotifier, optional
        The mocked returned value from IObserver.get_notifier
        If not provided, a dummy notifier is created.
    maintainer : INotifier, optional
        The mocked returned value from IObserver.get_maintainer
        if not provided, a dummy notifier is created.
    extra_graphs : iterable of ObserverGraph, optional
        The mocked yielded values from IObserver.iter_extra_graphs
    """

    def __init__(
            self,
            notify=True,
            observables=(),
            next_objects=(),
            notifier=None,
            maintainer=None,
            extra_graphs=()):

        if notifier is None:
            notifier = DummyNotifier()
        if maintainer is None:
            maintainer = DummyNotifier()

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
