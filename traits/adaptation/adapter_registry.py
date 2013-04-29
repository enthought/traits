""" A manager for adapter factories. """


from heapq import heappop, heappush
import inspect

from traits.api import Dict, HasTraits, Property

def type_distance(from_, to):
    if not issubclass(from_ ,to):
        return None

    distance = 0
    for t in inspect.getmro(from_):
        if not issubclass(t, to):
            return distance
        distance += 1

    print 'You should not be here'
    return distance


class AdapterRegistry(HasTraits):
    """ A manager for adapter factories. """

    #### 'AdapterRegistry' protocol ###########################################

    # All registered type-scope factories by the type of object that they
    # adapt.
    #
    # The dictionary is keyed by the *name* of the class rather than the class
    # itself to allow for adapter factory proxies to register themselves
    # without having to load and create the factories themselves (i.e., to
    # allow us to lazily load adapter factories contributed by plugins). This
    # is a slight compromise as it is obviously geared towards use in Envisage,
    # but it doesn't affect the API other than allowing a class OR a string to
    # be passed to 'register_adapters'.
    #
    # { String adaptee_class_name : List(AdapterFactory) factories }
    type_factories = Property(Dict)

    def _get_type_factories(self):
        """ Returns all registered type-scope factories. """

        return self._type_factories.copy()

    #### Private interface ####################################################

    # All registered type-scope factories by the type of object that they
    # adapt.
    _type_factories = Dict

    #### Methods ##############################################################

    def adapt(self, adaptee, to_protocol, *args, **kw):
        """ Returns an adapter that adapts an object to a given protocol.

        'adaptee'     is the object that we want to adapt.
        'to_protocol' is the protocol that the adaptee should be adapted to.

        If 'adaptee' already provides the given protocol then it is simply
        returned unchanged.

        Returns None if 'adaptee' does NOT provide the given protocol and no
        adapter (or chain of adapters) exists to adapt it.

        """

        # If the object is already provides the given protocol then it is
        # simply returned.
        if isinstance(adaptee, to_protocol):
            result = adaptee

        # Otherwise, look at each class in the adaptee's MRO to see if there
        # is an adapter factory registered that can adapt the object to the
        # target class.
        else:
            result = self._adapt_type(adaptee, to_protocol, *args, **kw)

        return result

    def register_type_adapters(self, factory):
        """ Registers a type-scope adapter factory.

        'adaptee_class' can be either a class object or the name of a class.

        A factory can be in exactly one manager (as it uses the manager's type
        system).

        """

        from_protocol = factory.from_protocol
        
        if isinstance(from_protocol, basestring):
            from_protocol_name = from_protocol

        else:
            from_protocol_name = self._get_class_name(from_protocol)

        factories = self._type_factories.setdefault(from_protocol_name, [])
        factories.append(factory)

        return

    #### Private protocol ######################################################

    def _adapt_type(self, adaptee, target_class, *args, **kw):
        """ Returns an adapter that adapts an object to the target class.

        Returns None if no such adapter exists.

        """

        print '------------------------ adapy type', adaptee, target_class
        print 'type facvtories', self._type_factories
        
        factories_queue = []
        for factories in self._type_factories.values():
            for factory in factories:
                distance = type_distance(type(adaptee), factory.from_protocol)

                if distance is not None:
                    heappush(factories_queue, (distance, adaptee, factory))

        print 'adaptee', adaptee, type(adaptee)
        print '-----------factories', factories_queue
        
        while len(factories_queue) > 0:
            print factories_queue
            distance, obj, factory = heappop(factories_queue)
            print 'CONSIDERING', factory, 'DIST', distance

            adapter = factory.adapt(obj, factory.to_protocol)
            print 'ADAPTER?', adapter
            if isinstance(adapter, target_class):
                break

            for factories in self._type_factories.values():
                for factory in factories:
                    extra_distance = type_distance(type(adapter), factory.from_protocol)

                    if extra_distance is not None:
                        heappush(factories_queue, (distance+extra_distance, adapter, factory))

        else:
            adapter = None

        return adapter
        
    def _get_class_name(self, klass):
        """ Returns the full class name for a class. """

        return "%s.%s" % (klass.__module__, klass.__name__)

#### EOF ######################################################################
