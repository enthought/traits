""" The abstract base class for adapter factories. """


from traits.api import Any, HasTraits

from apptools.adaptation.adapter_registry import AdapterRegistry


class AdapterFactory(HasTraits):
    """ The abstract base class for adapter factories. """

    # The adapter implementation.
    adapter_class = Any

    # Adapters created by the factory adapt from this protocol...
    from_protocol = Any

    # ... to this protocol.
    to_protocol = Any
    
    def adapt(self, obj, to_protocol):

        if not AdapterRegistry.provides_protocol(obj, self.from_protocol):
            return None

        if to_protocol is not self.to_protocol:
            return None
        
        return self.adapter_class(adaptee=obj)


    #### 'object' protocol ####################################################

    def __repr__(self):
        template = "Adapter factory: '{from_}' -> '{to}'"
        repr = template.format(
            from_ = self.from_protocol.__name__,
            to    = self.to_protocol.__name__
        )
        return repr

#### EOF ######################################################################
