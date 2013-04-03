""" The abstract base class for adapter factories. """


from traits.api import Any, HasTraits


class AdapterFactory(HasTraits):
    """ The abstract base class for adapter factories. """

    # The adapter implementation.
    adapter_class = Any

    # Adapters created by the factory adapt from this protocol...
    from_protocol = Any

    # ... to this protocol.
    to_protocol = Any
    
    def adapt(self, obj, to_protocol):
        if not isinstance(obj, self.from_protocol):
            return None

        if to_protocol is not self.to_protocol:
            return None
        
        return self.adapter_class(adaptee=obj)

#### EOF #######################################################################
