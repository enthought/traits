# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Manages all registered adaptations. """


from heapq import heappop, heappush
import inspect
import itertools
import functools

from traits.adaptation.adaptation_error import AdaptationError
from traits.has_traits import HasTraits
from traits.trait_types import Dict, List, Str


def no_adapter_necessary(adaptee):
    """ An adapter factory used to register that a protocol provides another.

    See 'register_provides' for details.

    """

    return adaptee


class AdaptationManager(HasTraits):
    """ Manages all registered adaptations. """

    #### 'AdaptationManager' class protocol ###################################

    @staticmethod
    def mro_distance_to_protocol(from_type, to_protocol):
        """ Return the distance in the MRO from 'from_type' to 'to_protocol'.

        If `from_type` provides `to_protocol`, returns the distance between
        `from_type` and the super-most class in the MRO hierarchy providing
        `to_protocol` (that's where the protocol was provided in the first
        place).

        If `from_type` does not provide `to_protocol`, return None.

        """

        if not AdaptationManager.provides_protocol(from_type, to_protocol):
            return None

        # We walk up the MRO hierarchy until the point where the `to_protocol`
        # is *no longer* provided. When we reach that point we know that the
        # previous class in the MRO is the one that provided the protocol in
        # the first place (e.g., the first super-class implementing an
        # interface).
        supertypes = inspect.getmro(from_type)[1:]

        distance = 0
        for t in supertypes:
            if AdaptationManager.provides_protocol(t, to_protocol):
                distance += 1

            # We have reached the point in the MRO where the protocol is no
            # longer provided.
            else:
                break

        return distance

    @staticmethod
    def provides_protocol(type_, protocol):
        """ Does the given type provide (i.e implement) a given protocol?

        Parameters
        ----------
        type_
            Python 'type'.
        protocol
            Either a regular Python class or a traits Interface.

        Returns
        -------
        result : bool
            True if the object provides the protocol, otherwise False.

        """
        return issubclass(type_, protocol)

    #### 'AdaptationManager' protocol #########################################

    def adapt(self, adaptee, to_protocol, default=AdaptationError):
        """ Attempt to adapt an object to a given protocol.

        If *adaptee* already provides (i.e. implements) the given protocol
        then it is simply returned unchanged.

        Otherwise, we try to build a chain of adapters that adapt *adaptee* to
        *to_protocol*. If no such adaptation is possible then either an
        AdaptationError is raised, or *default* is returned.

        Parameters
        ----------
        adaptee : object
            The object that we want to adapt.
        to_protocol : type or interface
            The protocol that the want to adapt *adaptee* to.
        default : object, optional
            Object to return if no adaptation is possible. If no default is
            provided, and adaptation fails, an ``AdaptationError`` is raised.

        Returns
        -------
        adapted_object : to_protocol
            The original adaptee adapted to the target protocol.

        Raises
        ------
        AdaptationError
            If adaptation is not possible, and no default is given.
        """

        # If the object already provides the given protocol then it is
        # simply returned.
        if self.provides_protocol(type(adaptee), to_protocol):
            result = adaptee

        # Otherwise, try adapting the object.
        else:
            result = self._adapt(adaptee, to_protocol)

        if result is None:
            if default is AdaptationError:
                raise AdaptationError(
                    "Could not adapt %r to %r" % (adaptee, to_protocol)
                )
            else:
                result = default

        return result

    def register_offer(self, offer):
        """ Register an offer to adapt from one protocol to another. """

        offers = self._adaptation_offers.setdefault(
            offer.from_protocol_name, []
        )
        offers.append(offer)

    def register_factory(self, factory, from_protocol, to_protocol):
        """ Register an adapter factory.

        This is a simply a convenience method that creates and registers an
        'AdaptationOffer' from the given arguments.

        """

        from traits.adaptation.adaptation_offer import AdaptationOffer

        self.register_offer(
            AdaptationOffer(
                factory=factory,
                from_protocol=from_protocol,
                to_protocol=to_protocol,
            )
        )

    def register_provides(self, provider_protocol, protocol):
        """ Register that a protocol provides another. """

        self.register_factory(
            no_adapter_necessary, provider_protocol, protocol
        )

    def supports_protocol(self, obj, protocol):
        """ Does the object support a given protocol?

        An object "supports" a protocol if either it "provides" it directly,
        or it can be adapted to it.

        """

        return self.adapt(obj, protocol, None) is not None

    #### Private protocol #####################################################

    #: All registered adaptation offers.
    #: Keys are the type name of the offer's from_protocol; values are a
    #: list of adaptation offers.
    _adaptation_offers = Dict(Str, List)

    def _adapt(self, adaptee, to_protocol):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if no such adapter exists.

        """

        # The algorithm for finding a sequence of adapters adapting 'adaptee'
        # to 'to_protocol' is based on a weighted graph.

        # Nodes on the graphs are protocols (types or interfaces).
        # Edges are adaptation offers that connect a offer.from_protocol to a
        # offer.to_protocol.
        # Edges connect protocol A to protocol B and are weighted by two
        # numbers in this priority:
        # 1) a unit weight (1) representing the fact that we use 1 adaptation
        #    offer to go from A to B
        # 2) the number of steps up the type hierarchy that we need to take
        #    to go from A to offer.from_protocol, so that more specific
        #    adapters are always preferred

        # The algorithm finds the shortest weighted path between 'adaptee'
        # and 'to_protocol'. Once a candidate path is found, it tries to
        # create the adapters using the factories in the adaptation offers
        # that compose the path. If this fails because of conditional
        # adaptation (i.e., an adapter factory returns None), the path
        # is discarded and the algorithm looks for the next shortest path.

        # Cycles in adaptation are avoided by only considering path were
        # every adaptation offer is used at most once.

        # The implementation of the algorithm is based on a priority queue,
        # 'offer_queue'.
        #
        # Each value in the queue has got two parts,
        # one is the adaptation path, i.e., the sequence of adaptation offers
        # followed so far; the second value is the protocol of the last
        # visited node.
        #
        # The priority in the queue is the sum of all the weights for the
        # edges traversed in the path.

        # Unique sequence counter to make the priority list stable
        # w.r.t the sequence of insertion.
        counter = itertools.count()

        # The priority queue containing entries of the form
        # (cumulative weight, path, current protocol) describing an
        # adaptation path starting at `adaptee`, following a sequence
        # of adaptation offers, `path`, and having weight `cumulative_weight`.
        #
        # 'cumulative weight' is a tuple of the form
        # (number of traversed adapters,
        #  number of steps up protocol hierarchies,
        #  counter)
        #
        # The counter is an increasing number, and is used to make the
        # priority queue stable w.r.t insertion time
        # (see http://bit.ly/13VxILn).
        offer_queue = [((0, 0, next(counter)), [], type(adaptee))]

        while len(offer_queue) > 0:
            # Get the most specific candidate path for adaptation.
            weight, path, current_protocol = heappop(offer_queue)

            edges = self._get_applicable_offers(current_protocol, path)

            # Sort by weight first, then by from_protocol type.
            edges.sort(
                key=functools.cmp_to_key(
                    _by_weight_then_from_protocol_specificity
                )
            )

            # At this point, the first edges are the shortest ones. Within
            # edges with the same distance, interfaces which are subclasses
            # of other interfaces in that group come first. The rest of
            # the order is unspecified.

            for mro_distance, offer in edges:
                new_path = path + [offer]

                # Check if we arrived at the target protocol.
                if self.provides_protocol(offer.to_protocol, to_protocol):
                    # Walk path and create adapters
                    adapter = adaptee
                    for offer in new_path:
                        adapter = offer.factory(adapter)
                        if adapter is None:
                            # This adaptation attempt failed (e.g. because of
                            # conditional adaptation).
                            # Discard this path and continue.
                            break

                    else:
                        # We're done!
                        return adapter

                else:
                    # Push the new path on the priority queue.
                    adapter_weight, mro_weight, _ = weight
                    new_weight = (
                        adapter_weight + 1,
                        mro_weight + mro_distance,
                        next(counter),
                    )
                    heappush(
                        offer_queue, (new_weight, new_path, offer.to_protocol)
                    )

        return None

    def _get_applicable_offers(self, current_protocol, path):
        """ Find all adaptation offers that can be applied to a protocol.

        Return all the applicable offers together with the number of steps
        up the MRO hierarchy that need to be taken from the protocol
        to the offer's from_protocol.
        The returned object is a list of tuples (mro_distance, offer) .

        In terms of our graph algorithm, we're looking for all outgoing edges
        from the current node.
        """

        edges = []

        for from_protocol_name, offers in self._adaptation_offers.items():
            from_protocol = offers[0].from_protocol
            mro_distance = self.mro_distance_to_protocol(
                current_protocol, from_protocol
            )

            if mro_distance is not None:

                for offer in offers:
                    # Avoid cycles by checking that we did not consider this
                    # offer in this path.
                    if offer not in path:
                        edges.append((mro_distance, offer))

        return edges


def _by_weight_then_from_protocol_specificity(edge_1, edge_2):
    """ Comparison function for graph edges.

    Each edge is of the form (mro distance, adaptation offer).

    Comparison is done by mro distance first, and by offer's from_protocol
    issubclass next.

    If two edges have the same mro distance, and the from_protocols of the
    two edges are not subclasses of one another, they are considered "equal".

    """

    # edge_1 and edge_2 are edges, of the form (mro_distance, offer)

    mro_distance_1, offer_1 = edge_1
    mro_distance_2, offer_2 = edge_2

    # First, compare the MRO distance.
    if mro_distance_1 < mro_distance_2:
        return -1
    elif mro_distance_1 > mro_distance_2:
        return 1

    # The distance is equal, prefer more specific 'from_protocol's
    if offer_1.from_protocol is offer_2.from_protocol:
        return 0

    if issubclass(offer_1.from_protocol, offer_2.from_protocol):
        return -1
    elif issubclass(offer_2.from_protocol, offer_1.from_protocol):
        return 1

    return 0


#: The default global adaptation manager.
#:
#: PROVIDED FOR BACKWARD COMPATIBILITY ONLY, IT SHOULD NEVER BE USED DIRECTLY.
#: If you must use a global adaptation manager, use the functions
#: :class:`get_global_adaptation_manager`,
#: :class:`reset_global_adaptation_manager`,
#: :class:`set_global_adaptation_manager`.

adaptation_manager = AdaptationManager()


def set_global_adaptation_manager(new_adaptation_manager):
    """ Set the global adaptation manager to the given instance. """
    global adaptation_manager
    adaptation_manager = new_adaptation_manager


def reset_global_adaptation_manager():
    """ Set the global adaptation manager to a new AdaptationManager instance.
    """
    global adaptation_manager
    adaptation_manager = AdaptationManager()


def get_global_adaptation_manager():
    """ Set a reference to the global adaptation manager. """
    global adaptation_manager
    return adaptation_manager


# Convenience references to methods on the default adaptation manager.
#
# If you add a public method to the adaptation manager protocol then don't
# forget to add a convenience function here!


def adapt(adaptee, to_protocol, default=AdaptationError):
    """ Attempt to adapt an object to a given protocol. """
    manager = get_global_adaptation_manager()
    return manager.adapt(adaptee, to_protocol, default)


def register_factory(factory, from_protocol, to_protocol):
    """ Register an adapter factory. """
    manager = get_global_adaptation_manager()
    return manager.register_factory(factory, from_protocol, to_protocol)


def register_offer(offer):
    """ Register an offer to adapt from one protocol to another. """
    manager = get_global_adaptation_manager()
    return manager.register_offer(offer)


def register_provides(provider_protocol, protocol):
    """ Register that a protocol provides another. """
    manager = get_global_adaptation_manager()
    return manager.register_provides(provider_protocol, protocol)


def supports_protocol(obj, protocol):
    """ Does the object support a given protocol? """
    manager = get_global_adaptation_manager()
    return manager.supports_protocol(obj, protocol)


def provides_protocol(type_, protocol):
    """ Does the given type provide (i.e implement) a given protocol? """
    return AdaptationManager.provides_protocol(type_, protocol)
