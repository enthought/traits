""" A manager for adapter factories. """


from heapq import heappop, heappush
import inspect

from traits.api import HasTraits, Interface, List, Property


class AdapterRegistry(HasTraits):
    """ A manager for adapter factories. """

    #### 'AdapterRegistry' class protocol #####################################

    @staticmethod
    def mro_distance_to_protocol(from_type, to_protocol):
        """ If `from_type` provides `to_protocol`, returns the distance between
        `from_type` and the super-most class in the MRO hierarchy providing
        `to_protocol` (that's where the protocol was provided in the first place).

        If `from_type` does not provide `to_protocol`, return None.
        """

        if not AdapterRegistry.provides_protocol(from_type ,to_protocol):
            return None

        # We walk up the MRO hierarchy until the point where the `to_protocol`
        # is no longer provided. That's where the protocol was provided in
        # the first place (e.g., the first super-class implementing an interface).
        distance = 0
        for t in inspect.getmro(from_type):
            if not AdapterRegistry.provides_protocol(t, to_protocol):
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

    #### 'AdapterRegistry' protocol ###########################################

    # List of registered adapter factories.
    adapter_factories = Property(List)

    def _get_adapter_factories(self):
        """ Trait property getter. """

        return list(self._adapter_factories)

    #### Private interface ####################################################

    # All registered type-scope factories by the type of object that they
    # adapt.
    _adapter_factories = List

    #### Methods ##############################################################

    def adapt(self, adaptee, to_protocol):
        """ Returns an adapter that adapts an object to a given protocol.

        'adaptee'     is the object that we want to adapt.
        'to_protocol' is the protocol that the adaptee should be adapted to.

        If 'adaptee' already provides the given protocol then it is simply
        returned unchanged.

        Returns None if 'adaptee' does NOT provide the given protocol and no
        adapter (or chain of adapters) exists to adapt it.

        """

        # If the object already provides the given protocol then it is
        # simply returned.
        if self.provides_protocol(type(adaptee), to_protocol):
            result = adaptee

        # Otherwise, look at each class in the adaptee's MRO to see if there
        # is an adapter factory registered that can adapt the object to the
        # target class.
        else:
            result = self._adapt_type(adaptee, to_protocol)

        return result

    def register_adapter_factory(self, factory, from_protocol, to_protocol):
        """ Registers an adapter factory. """

        from apptools.adaptation.adapter_factory import AdapterFactory

        offer = AdapterFactory(
            factory       = factory,
            from_protocol = from_protocol,
            to_protocol   = to_protocol
        )

        self._adapter_factories.append(offer)

        return

    #### Private protocol ######################################################

    def _adapt_type(self, adaptee, target_class):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if no such adapter exists.

        """


        SUBCLASS_WEIGHT = 1e-9

        print '------------------------ adapt type', adaptee, target_class
        print 'type factories', self._adapter_factories


        # `factories_queue` is a priority queue. The values in the queue are
        # tuples (adapter, factory). `factory` is the factory used to get
        # from `adaptee` to `adapter` along the chain.
        # The priority in the priority queue corresponds to
        # the number of steps that it took to go from `adaptee` to `adapter`.
        # In order to prefer adaptation paths that do start at the most
        # specific classes along the chain, we add a small factor
        # (SUBCLASS_WEIGHT) for each step up the MRO hierarchy that we need
        # to take.

        # In other words, we are considering a weighted graph of all classes.
        # Parent and child classes are connected with edges with a small weight
        # SUBCLASS_WEIGHT, classes related by adaptation are connected
        # with edges of weight 1.0 .

        # SUBCLASS_WEIGHT is small enough that it would take a hierarchy
        # or a billion objects to weight as much as one adaptation step.

        factories_queue = []
        for factory in self._adapter_factories:
            distance = self.mro_distance_to_protocol(
                type(adaptee), factory.from_protocol
            )
            print 'TYPE DIST', distance
            if distance is not None:
                weight = distance * SUBCLASS_WEIGHT + 1.0
                heappush(factories_queue, (weight, adaptee, factory))

        print 'adaptee', adaptee, type(adaptee)
        print '-----------factories', factories_queue
        
        while len(factories_queue) > 0:
            print factories_queue
            weight, obj, factory = heappop(factories_queue)
            print 'CONSIDERING', factory, 'WEIGHT', weight

            adapter = factory.adapt(obj, factory.to_protocol)
            print 'ADAPTER?', adapter
            if self.provides_protocol(type(adapter), target_class):
                break

            for factory in self._adapter_factories:
                distance = self.mro_distance_to_protocol(
                    type(adapter), factory.from_protocol
                )
                if distance is not None:
                    total_weight = weight + 1.0 + distance * SUBCLASS_WEIGHT
                    heappush(
                        factories_queue,
                        (total_weight, adapter, factory)
                    )

        else:
            adapter = None

        return adapter
        
    def _get_class_name(self, klass):
        """ Returns the full class name for a class. """

        return "%s.%s" % (klass.__module__, klass.__name__)


adapter_registry = AdapterRegistry()


def register_adapter_factory(factory, from_protocol, to_protocol):

    adapter_registry.register_adapter_factory(
        factory, from_protocol, to_protocol
    )

    return

#### EOF ######################################################################
