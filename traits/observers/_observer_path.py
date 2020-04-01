# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!


class ObserverPath:
    """ An ``ObserverPath`` is an object for describing what traits are being
    observed on an instance of ``HasTraits``.

    The most basic unit in a path is a node, which is a context specific
    observer. For example, a node can be an observer specialized in
    changes on a named trait, an observer specialized in
    changes on a number of traits matching a certain criteria, an observer
    specialized in mutations on a list, etc.

    The most basic example is an ``ObserverPath`` that contains only one node,
    e.g. for observing changes on a named trait.

    An ``ObserverPath`` can have branches, e.g. to observe more than one trait
    on a nested object. The attribute ``nexts`` represents these branches.
    Each item in ``nexts`` is another ``ObserverPath``.

    In most use cases, an ``ObserverPath`` represents a rooted directed acyclic
    graph. To support an existing feature of recursion in the old
    ``on_trait_change`` machinery, an ``ObserverPath`` is allowed loops
    (i.e. an edge that connects a node to itself). Hence the implementations
    assumes ``ObserverPath`` is a rooted directed almost-acyclic graph with
    loops.

    In order to (1) avoid hooking up a user callback with the same observer
    twice, and (2) remove an observer when they are not needed, once an
    ``ObserverPath`` object is constructed (e.g. after mutating ``nexts``
    for constructing branches) and is ready to be used against an instance
    of ``HasTraits``, it should not be mutated again.

    For the same reason, ``ObserverPath`` implements ``__hash__`` and
    ``__eq__`` and requires its nodes to also support these methods.

    An ``ObserverPath`` does not keep states regarding the HasTraits instances
    and the user callbacks it was used with. An ``ObserverPath`` can be
    reused multiple times on different ``HasTraits`` instance and with
    different user callback.

    This object is considered a low-level object for the observer mechanism.
    It is not intended to be instantiated by users directly. Users will be
    given higher-level wrappers for creating ``ObserverPath`` objects.
    """

    def __init__(self, node, nexts=None):
        """
        Parameters
        ----------
        node : any
            A context specific observer.
            It must be a hashable object. In practice, this will be
            an instance that implements ``IObserver``.
        nexts : iterable of ObserverPath
            Branches on this path.
        """
        self.node = node

        self.nexts = set(nexts) if nexts is not None else set()

    def __hash__(self):
        """ Return the hash of this ObserverPath."""
        return hash(
            (type(self), self.node, hash(frozenset(self.nexts)))
        )

    def __eq__(self, other):
        """ Return true if another object is an ObserverPath with the
        same content.
        """
        if other is self:
            return True
        if type(self) is not type(other):
            return False
        if self.node != other.node:
            return False
        if len(self.nexts) != len(other.nexts):
            return False

        # Remove loops
        self_nexts = set(path for path in self.nexts if path is not self)
        other_nexts = set(path for path in other.nexts if path is not other)
        if len(self_nexts) != len(other_nexts):
            return False
        # Paths are hashable.
        return self_nexts == other_nexts
