""" Manages all registered adaptations. """


from heapq import heappop, heappush
import inspect
import itertools

from traits.api import Dict, HasTraits, Interface, List, Str
from traits.has_traits import __NoInterface__


class AdaptationError(TypeError):
    """ Exception raised when a requested adaptation is not possible. """

    pass


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

        'type_'    is a Python 'type'.
        'protocol' is either a regular Python class or a traits Interface.

        Return True if the object provides the protocol, otherwise False.

        """

        if type_ is protocol:
            return True

        # Support for traits Interfaces
        if issubclass(protocol, Interface):
            if (hasattr(type_, '__implements__')
                and type_.__implements__ is not __NoInterface__):
                provides_protocol = issubclass(type_.__implements__, protocol)

            else:
                provides_protocol = issubclass(type_, protocol)

        # Support for regular ol' Python types (including ABCs).
        else:
            provides_protocol = issubclass(type_, protocol)

        return provides_protocol

    #### 'AdaptationManager' protocol ##########################################

    def adapt(self, adaptee, to_protocol, default=AdaptationError):
        """ Attempt to adapt an object to a given protocol.

        `adaptee`     is the object that we want to adapt.
        `to_protocol` is the protocol that the want to adapt the object to.

        If `adaptee` already provides (i.e. implements) the given protocol
        then it is simply returned unchanged.

        Otherwise, we try to build a chain of adapters that adapt `adaptee`
        to `to_protocol`.

        If no such adaptation is possible then either an AdaptationError is
        raised (if default=Adaptation error), or `default` is returned (as
        in the default value passed to 'getattr' etc).

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
                raise AdaptationError
            else:
                result = default

        return result

    def register_adaptation_offer(self, offer):
        """ Register an offer to adapt from one protocol to another. """

        from_protocol_name = self._get_type_name(offer.from_protocol)

        offers = self._adaptation_offers.setdefault(from_protocol_name, [])
        offers.append(offer)

        return

    def register_adapter_factory(self, factory, from_protocol, to_protocol):
        """ Register an adapter factory.

        This is a simply a convenience method that creates and registers an
        'AdaptationOffer' from the given arguments.

        """

        from apptools.adaptation.adaptation_offer import AdaptationOffer

        self.register_adaptation_offer(
            AdaptationOffer(
                factory       = factory,
                from_protocol = from_protocol,
                to_protocol   = to_protocol
            )
        )

        return

    def supports_protocol(self, obj, protocol):
        """ Does object support a given protocol?

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

        # `offer_queue` is a priority queue. The values in the queue are
        # tuples (adapter, offer). `offer` is the adaptation offer used to get
        # from `adaptee` to `adapter` along the chain.
        # The priority in the priority queue is a tuple: the first element is
        # the number of steps that it took to go from `adaptee` to `adapter`.
        # The second number is the number of step the type hierarchy that we
        # need to take, so that more specific adapters are always preferred.

        # In other words, we are considering a weighted graph of all classes.
        # The adaptation path from `adaptee` to `to_protocol` is the shortest
        # weighted path in this graph.
        # The weights are 1 for each adapter we have to apply; parent and
        # child classes are connected with edges with a very small weight
        # (infinitesimally small).

        # Warning: The criterion for an outgoing edge being already visited
        # is that the adaptation offer (adapter factory, from, to protocol)
        # has been already used successfully once. In a very strange adaptation
        # graph, the application of an adaptation offer might lead to the
        # target protocol at a later point in time (e.g., if the adapters have
        # side effects on creation).
        # All the examples we considered for this case turn out to be
        # exceptionally bad designs of adapters, so we think these cases
        # can be safely regarded as irrelevant.

        # Unique sequence counter to make the priority list stable
        # w.r.t the sequence of insertion.
        counter = itertools.count()

        # The priority queue containing entries of the form
        # (cumulative weight, path, current protocol) describing the path
        # from `adaptee` to `adapter`.
        # 'cumulative weight' is of the form ''
        offer_queue = [((0, 0, next(counter)), [], type(adaptee))]

        while len(offer_queue) > 0:
            # Get the most specific candidate path for adaptation.
            path_weight, path, current_protocol = heappop(offer_queue)

            edges = self._get_outgoing_edges(current_protocol, path)

            # Sort by weight first, then by from_protocol hierarchy.
            edges.sort(cmp=_cmp_weight_then_from_protocol_specificity)

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
                        adapter = offer.factory(adaptee=adapter)
                        if adapter is None:
                            break
                    else:
                        return adapter

                    continue

                # Otherwise, push the new path on the priority queue.
                path_adapter_weight, path_mro_weight, path_count = path_weight
                total_weight = (path_adapter_weight + 1,
                                path_mro_weight + mro_distance,
                                next(counter))
                heappush(offer_queue, (total_weight, new_path, offer.to_protocol))

        return None

    def _get_type_name(self, type_or_type_name):
        """ Returns the full dotted path for a type.

        For example:
        from traits.api import HasTraits
        _get_type_name(HasTraits) == 'traits.has_traits.HasTraits'

        If the type is given as a string (e.g., for lazy loading), it is just
        returned.

        """

        if isinstance(type_or_type_name, basestring):
            type_name = type_or_type_name

        else:
            type_name = "{}.{}".format(
                type_or_type_name.__module__, type_or_type_name.__name__
            )

        return type_name

    def _get_outgoing_edges(self, type_current_obj, path):

        edges = []

        for from_protocol_name, offers in self._adaptation_offers.items():
            from_protocol = offers[0].from_protocol
            mro_distance = self.mro_distance_to_protocol(
                type_current_obj, from_protocol
            )

            if mro_distance is not None:

                for offer in offers:
                    if offer not in path:
                        edges.append((mro_distance, offer))

        return edges


def _cmp_weight_then_from_protocol_specificity(edge_1, edge_2):
    # edge_1 and edge_2 are edges, of the form (mro_distance, offer)

    edge_1_mro_distance, edge_1_offer = edge_1
    edge_2_mro_distance, edge_2_offer = edge_2

    # First, compare the MRO distance.
    if edge_1_mro_distance < edge_2_mro_distance:
        return -1
    elif edge_1_mro_distance > edge_2_mro_distance:
        return 1

    # The distance is equal, prefer more specific 'from_protocol's
    if edge_1_offer.from_protocol is edge_2_offer.from_protocol:
        return 0

    if issubclass(edge_1_offer.from_protocol, edge_2_offer.from_protocol):
        return -1
    elif issubclass(edge_2_offer.from_protocol, edge_1_offer.from_protocol):
        return 1

    return 0


#: The default global adaptation manager.
adaptation_manager = AdaptationManager()

# Convenience functions acting on the default adaptation manager.
#
# If you add a public method to the adaptation manager protocol then don't
# forget to add a convenience function here!
def adapt(adaptee, to_protocol, default=AdaptationError):
    """ Attempt to adapt an object to a given protocol.

    `adaptee`     is the object that we want to adapt.
    `to_protocol` is the protocol that the want to adapt the object to.

    If `adaptee` already provides (i.e. implements) the given protocol
    then it is simply returned unchanged.

    Otherwise, we try to build a chain of adapters that adapt `adaptee`
    to `to_protocol`.

    If no such adaptation is possible then either an AdaptationError is
    raised (if default=AdaptationError), or `default` is returned (as
    in the default value passed to 'getattr' etc).

    """

    return adaptation_manager.adapt(adaptee, to_protocol, default=default)

def register_adaptation_offer(offer):
    """ Register an offer to adapt from one protocol to another. """

    adaptation_manager.register_adaptation_offer(offer)

    return

def register_adapter_factory(factory, from_protocol, to_protocol):
    """ Register an adapter factory.

    This is a simply a convenience method that creates and registers an
    'AdaptationOffer' from the given arguments.

    """

    adaptation_manager.register_adapter_factory(
        factory, from_protocol, to_protocol
    )

    return

def supports_protocol(obj, protocol):
    """ Does object support a given protocol?

    An object "supports" a protocol if either it "provides" it directly,
    or it can be adapted to it.

    """

    return adaptation_manager.supports_protocol(obj, protocol)

#### EOF ######################################################################
