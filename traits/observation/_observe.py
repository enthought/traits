# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


def add_or_remove_notifiers(
        *, object, graph, handler, target, dispatcher, remove):
    """ Add/Remove notifiers on objects following the description on an
    ObserverGraph.

    All nodes in ``ObserverGraph`` are required to be instances of
    ``IObserver``. The interface of ``IObserver`` supports this function.

    Parameters
    ----------
    object : object
        An object to be observed.
    graph : ObserverGraph
        A graph describing what and how extended traits are being observed.
        All nodes must be ``IObserver``.
    handler : callable(event)
        User-defined callable to handle change events.
        ``event`` is an object representing the change.
        Its type and content depends on the change.
    target : Any
        An object for defining the context of the user's handler notifier.
        This is typically an instance of HasTraits seen by the user as the
        "owner" of the observer.
    dispatcher : callable(callable, event)
        Callable for dispatching the user-defined handler, i.e. dispatching
        callback on a different thread.
    remove : boolean
        If true, notifiers are being removed.

    Raises
    ------
    NotiferNotFound
        Raised when notifier cannot be found for removal.
    """
    callable_ = _AddOrRemoveNotifier(
        object=object,
        graph=graph,
        handler=handler,
        target=target,
        dispatcher=dispatcher,
        remove=remove,
    )
    callable_()


class _AddOrRemoveNotifier:
    """ Callable for adding or removing notifiers.

    See ``add_or_remove_notifiers`` for the input parameters.
    """

    def __init__(self, *, object, graph, handler, target, dispatcher, remove):
        self.object = object
        self.graph = graph
        self.handler = handler
        self.target = target
        self.dispatcher = dispatcher
        self.remove = remove

        # list of (notifier, observable)
        self._processed = []

    def __call__(self):
        """ Main function for adding/removing notifiers.
        """

        # The order of events does not matter as they are independent of each
        # other.
        steps = [
            self._add_or_remove_notifiers,
            self._add_or_remove_maintainers,
            self._add_or_remove_children_notifiers,
            self._add_or_remove_extra_graphs,
        ]

        # Not quite the complete reversal, as trees are still walked from
        # root to leaves.
        if self.remove:
            steps = steps[::-1]

        try:
            for step in steps:
                step()
        except Exception:
            # Undo and then reraise
            while self._processed:
                notifier, observable = self._processed.pop()
                if self.remove:
                    notifier.add_to(observable)
                else:
                    notifier.remove_from(observable)
            raise
        else:
            self._processed.clear()

    def _add_or_remove_extra_graphs(self):
        """ Add or remove additional ObserverGraph contributed by the root
        observer. e.g. for handing trait_added event.
        """
        for extra_graph in self.graph.node.iter_extra_graphs(self.graph):
            add_or_remove_notifiers(
                object=self.object,
                graph=extra_graph,
                handler=self.handler,
                target=self.target,
                dispatcher=self.dispatcher,
                remove=self.remove,
            )

    def _add_or_remove_children_notifiers(self):
        """ Recursively add or remove notifiers for the children ObserverGraph.
        """
        for child_graph in self.graph.children:
            for next_object in self.graph.node.iter_objects(self.object):
                add_or_remove_notifiers(
                    object=next_object,
                    graph=child_graph,
                    handler=self.handler,
                    target=self.target,
                    dispatcher=self.dispatcher,
                    remove=self.remove,
                )

    def _add_or_remove_maintainers(self):
        """ Add or remove notifiers for maintaining children notifiers when
        the objects being observed by the root observer change.
        """
        for observable in self.graph.node.iter_observables(self.object):

            for child_graph in self.graph.children:

                change_notifier = self.graph.node.get_maintainer(
                    graph=child_graph,
                    handler=self.handler,
                    target=self.target,
                    dispatcher=self.dispatcher,
                )
                if self.remove:
                    change_notifier.remove_from(observable)
                else:
                    change_notifier.add_to(observable)

                self._processed.append((change_notifier, observable))

    def _add_or_remove_notifiers(self):
        """ Add or remove user notifiers for the objects observed by the root
        observer.
        """
        if not self.graph.node.notify:
            return

        for observable in self.graph.node.iter_observables(self.object):

            notifier = self.graph.node.get_notifier(
                handler=self.handler,
                target=self.target,
                dispatcher=self.dispatcher,
            )
            if self.remove:
                notifier.remove_from(observable)
            else:
                notifier.add_to(observable)

            self._processed.append((notifier, observable))
