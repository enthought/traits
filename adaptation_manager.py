""" Keeps a registry of available adaptation paths and handles adaptation. """


from heapq import heappop, heappush
import inspect

from traits.api import HasTraits, Instance, Interface, List


class AdaptationError(TypeError):
    pass


class AdaptationManager(HasTraits):
    """ Keeps a registry of available adaptation paths and handles adaptation.
    """

    #### 'AdaptationManager' class protocol ###################################

    @staticmethod
    def mro_distance_to_protocol(from_type, to_protocol):
        """ If `from_type` provides `to_protocol`, returns the distance between
        `from_type` and the super-most class in the MRO hierarchy providing
        `to_protocol` (that's where the protocol was provided in the first
        place).

        If `from_type` does not provide `to_protocol`, return None.
        """

        if not AdaptationManager.provides_protocol(from_type ,to_protocol):
            return None

        # We walk up the MRO hierarchy until the point where the `to_protocol`
        # is no longer provided. That's where the protocol was provided in
        # the first place (e.g., the first super-class implementing an
        # interface).
        distance = 0
        supertypes = inspect.getmro(from_type)[1:]
        for t in supertypes:
            if not AdaptationManager.provides_protocol(t, to_protocol):
                break
            distance += 1

        return distance

    @staticmethod
    def provides_protocol(type_, protocol):
        """ Does object implement a given protocol?

        'protocol' is either an Interface or a class.

        Return True if the object implements the interface, or is an instance
        of the class.
        """

        if issubclass(protocol, Interface):
            # support for traits' Interfaces
            if hasattr(type_, '__implements__'):
                provides_protocol = issubclass(type_.__implements__, protocol)
            else:
                provides_protocol = False

        else:
            # 'protocol' is a class
            provides_protocol = issubclass(type_, protocol)

        return provides_protocol

    #### Private interface ####################################################

    #: All registered adaptation offers.
    _adaptation_offers = List(Instance('apptools.adaptation.adaptation_offer.AdaptationOffer'))

    #### Methods ##############################################################

    def adapt(self, adaptee, to_protocol, default=AdaptationError):
        """ Returns an adapter that adapts an object to a given protocol.

        `adaptee`     is the object that we want to adapt.
        `to_protocol` is the protocol that the adaptee should be adapted to.

        If `adaptee` already provides the given protocol then it is simply
        returned unchanged. Otherwise, we try to build a chain of adapters
        that adapt `adaptee` to `to_protocol`.

        If no such chain exists, an AdaptationError is raised unless a
        `default` return value is specified.

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
        """ Register an adaptation offer. """

        self._adaptation_offers.append(offer)

        return

    def register_adapter_factory(self, factory, from_protocol, to_protocol):
        """ Register an adapter factory.

        This is a convenience method that creates an AdaptationOffer instance
        from the given arguments and registers it.

        """

        from apptools.adaptation.adaptation_offer import AdaptationOffer

        offer = AdaptationOffer(
            factory       = factory,
            from_protocol = from_protocol,
            to_protocol   = to_protocol
        )

        self.register_adaptation_offer(offer)

        return

    def supports_protocol(self, obj, protocol):
        """ Does object support a given protocol?

        An object "supports" a protocol if either it "provides" it, or if
        can be adapted to it.

        """

        return self.adapt(obj, protocol, None) is not None

    #### Private protocol #####################################################

    _SUBCLASS_WEIGHT = 1e-9

    def _adapt(self, adaptee, to_protocol):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if no such adapter exists.

        """

        # `offer_queue` is a priority queue. The values in the queue are
        # tuples (adapter, offer). `offer` is the adaptation offer used to get
        # from `adaptee` to `adapter` along the chain.
        # The priority in the priority queue corresponds to
        # the number of steps that it took to go from `adaptee` to `adapter`.
        # In order to prefer adaptation paths that do start at the most
        # specific classes along the chain, we add a small factor
        # (SUBCLASS_WEIGHT) for each step up the type hierarchy that we need
        # to take.

        # In other words, we are considering a weighted graph of all classes.
        # Parent and child classes are connected with edges with a small weight
        # SUBCLASS_WEIGHT, classes related by adaptation are connected
        # with edges of weight 1.0 . The adaptation path from `adaptee`
        # to `to_protocol` is the shortest weighted path in this graph.

        # SUBCLASS_WEIGHT is small enough that it would take a hierarchy
        # a billion classes deep to weigh as much as one adaptation step. :-)

        visited = set()
        offer_queue = []

        self._get_outgoing_edges(offer_queue, visited, adaptee, 0.0)

        while len(offer_queue) > 0:
            # Get the most specific candidate path for adaptation.
            weight, obj, factory = heappop(offer_queue)
            visited.add(factory)

            adapter = factory.adapt(obj, factory.to_protocol)
            # Check if we arrived at the target protocol.
            if self.provides_protocol(type(adapter), to_protocol):
                break

            self._get_outgoing_edges(offer_queue, visited, adapter, weight+1.0)

        else:
            adapter = None

        return adapter

    def _get_outgoing_edges(self, queue, visited, obj, current_weight):

        for offer in self._adaptation_offers:
            if offer in visited:
                continue

            distance = self.mro_distance_to_protocol(
                type(obj), offer.from_protocol
            )

            if distance is not None:
                weight = distance * self._SUBCLASS_WEIGHT + current_weight
                heappush(queue, (weight, obj, offer))


#: Default global adaptation manager.
adaptation_manager = AdaptationManager()


# Convenience functions acting on the default adaptation manager.

def adapt(adaptee, to_protocol, default=AdaptationError):

    return adaptation_manager.adapt(adaptee, to_protocol, default=default)


def register_adaptation_offer(offer):

    adaptation_manager.register_adaptation_offer(offer)

    return


def register_adapter_factory(factory, from_protocol, to_protocol):

    adaptation_manager.register_adapter_factory(
        factory, from_protocol, to_protocol
    )

    return


def supports_protocol(obj, protocol):

    return adaptation_manager.supports_protocol(obj, protocol)

#### EOF ######################################################################
