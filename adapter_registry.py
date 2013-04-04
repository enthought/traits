""" A manager for adapter factories. """


from heapq import heappop, heappush

from traits.api import HasTraits, Interface, List, Property


class AdapterRegistry(HasTraits):
    """ A manager for adapter factories. """

    #### 'AdapterRegistry' class protocol #####################################

    @staticmethod
    def provides_protocol(obj, protocol):
        """ Does object implement a given protocol?

        'protocol' is either an Interface or a class.

        Return True if the object implements the interface, or is an instance
        of the class.
        """

        if issubclass(protocol, Interface):
            # support for traits' Interfaces
            if hasattr(obj, '__implements__'):
                provides_protocol = issubclass(obj.__implements__, protocol)
            else:
                provides_protocol = False

        else:
            # 'protocol' is a class
            provides_protocol = isinstance(obj, protocol)

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
        if self.provides_protocol(adaptee, to_protocol):
            result = adaptee

        # Otherwise, look at each class in the adaptee's MRO to see if there
        # is an adapter factory registered that can adapt the object to the
        # target class.
        else:
            result = self._adapt_type(adaptee, to_protocol)

        return result

    def register_adapter_factory(self, factory):
        """ Registers an adapter factory. """

        self._adapter_factories.append(factory)

        return

    #### Private protocol ######################################################

    def _adapt_type(self, adaptee, target_class):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if no such adapter exists.

        """

        print '------------------------ adapt type', adaptee, target_class
        print 'type factories', self._adapter_factories

        factories_queue = []
        for factory in self._adapter_factories:
            if self.provides_protocol(adaptee, factory.from_protocol):
                heappush(factories_queue, (1, adaptee, factory))

        print 'adaptee', adaptee, type(adaptee)
        print '-----------factories', factories_queue
        
        while len(factories_queue) > 0:
            print factories_queue
            distance, obj, factory = heappop(factories_queue)
            print 'CONSIDERING', factory, 'DIST', distance

            adapter = factory.adapt(obj, factory.to_protocol)
            print 'ADAPTER?', adapter
            if self.provides_protocol(adapter, target_class):
                break

            for factory in self._adapter_factories:
                if self.provides_protocol(adapter, factory.from_protocol):
                    heappush(factories_queue, (distance+1, adapter, factory))

        else:
            adapter = None

        return adapter
        
    def _get_class_name(self, klass):
        """ Returns the full class name for a class. """

        return "%s.%s" % (klass.__module__, klass.__name__)

#### EOF ######################################################################
