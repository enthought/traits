# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


def add_notifiers(*, object, graph, handler, target, dispatcher):
    callable_ = _AddNotifier(
        object=object,
        graph=graph,
        handler=handler,
        target=target,
        dispatcher=dispatcher,
    )
    callable_()


def remove_notifiers(*, object, graph, handler, target, dispatcher):
    callable_ = _RemoveNotifier(
        object=object,
        graph=graph,
        handler=handler,
        target=target,
        dispatcher=dispatcher,
    )
    callable_()


class _AddNotifier:
    def __init__(self, *, object, graph, handler, target, dispatcher):
        self.object = object
        self.graph = graph
        self.handler = handler
        self.target = target
        self.dispatcher = dispatcher

        # list of (notifier, observable)
        self._processed = []

    def __call__(self):
        # The order of events does not matter as they are independent of each
        # other.
        steps = [
            self._add_notifiers,
            self._add_maintainers,
            self._add_children_notifiers,
            self._add_extra_graphs,
        ]

        try:
            for step in steps:
                step()
        except Exception:
            # Undo and then reraise
            while self._processed:
                notifier, observable = self._processed.pop()
                notifier.remove_from(observable)
            raise
        else:
            self._processed.clear()

    def _add_extra_graphs(self):
        """ Add or remove additional ObserverGraph contributed by the root
        observer. e.g. for handing trait_added event.
        """
        for extra_graph in self.graph.node.iter_extra_graphs(self.graph):
            add_notifiers(
                object=self.object,
                graph=extra_graph,
                handler=self.handler,
                target=self.target,
                dispatcher=self.dispatcher,
            )

    def _add_children_notifiers(self):
        """ Recursively add or remove notifiers for the children ObserverGraph.
        """
        for child_graph in self.graph.children:
            for next_object in self.graph.node.iter_objects(self.object):
                add_notifiers(
                    object=next_object,
                    graph=child_graph,
                    handler=self.handler,
                    target=self.target,
                    dispatcher=self.dispatcher,
                )

    def _add_maintainers(self):
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
                change_notifier.add_to(observable)

                self._processed.append((change_notifier, observable))

    def _add_notifiers(self):
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
            notifier.add_to(observable)

            self._processed.append((notifier, observable))


class _RemoveNotifier:
    def __init__(self, *, object, graph, handler, target, dispatcher):
        self.object = object
        self.graph = graph
        self.handler = handler
        self.target = target
        self.dispatcher = dispatcher

        # list of (notifier, observable)
        self._processed = []

    def __call__(self):
        # The order of events does not matter as they are independent of each
        # other.
        steps = [
            self._remove_notifiers,
            self._remove_maintainers,
            self._remove_children_notifiers,
            self._remove_extra_graphs,
        ]

        # Not quite the complete reversal, as trees are still walked from
        # root to leaves.
        steps = steps[::-1]

        try:
            for step in steps:
                step()
        except Exception:
            # Undo and then reraise
            while self._processed:
                notifier, observable = self._processed.pop()
                notifier.add_to(observable)
            raise
        else:
            self._processed.clear()

    def _remove_extra_graphs(self):
        """ Add or remove additional ObserverGraph contributed by the root
        observer. e.g. for handing trait_added event.
        """
        for extra_graph in self.graph.node.iter_extra_graphs(self.graph):
            remove_notifiers(
                object=self.object,
                graph=extra_graph,
                handler=self.handler,
                target=self.target,
                dispatcher=self.dispatcher,
            )

    def _remove_children_notifiers(self):
        """ Recursively add or remove notifiers for the children ObserverGraph.
        """
        for child_graph in self.graph.children:
            for next_object in self.graph.node.iter_objects(self.object):
                remove_notifiers(
                    object=next_object,
                    graph=child_graph,
                    handler=self.handler,
                    target=self.target,
                    dispatcher=self.dispatcher,
                )

    def _remove_maintainers(self):
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
                change_notifier.remove_from(observable)

                self._processed.append((change_notifier, observable))

    def _remove_notifiers(self):
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
            notifier.remove_from(observable)

            self._processed.append((notifier, observable))
