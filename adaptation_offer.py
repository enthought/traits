""" An offer to create adapters from one protocol to another. """


from traits.api import Any, HasTraits, Property

from apptools.adaptation.adaptation_manager import AdaptationManager
from apptools.naming.initial_context import _import_symbol


class AdaptationOffer(HasTraits):
    """ An offer to create adapters from one protocol to another.

    An adaptation offer consists of a factory for an adapter, and the
    definition of the protocols from and to which an object can be adapted.

    """

    #### 'AdaptationOffer' protocol ###########################################

    #: A factory for adapters.
    #:
    #: The factory takes one argument, the object to be adapted, and returns
    #: an adapter from `from_protocol` to `to_protocol`.
    #:
    #: The factory can be specified as a callable object, or a string in the
    #: form 'foo.bar.baz' which is turned into an import statement
    #: 'from foo.bar import baz' and imported when this trait is first
    #: requested.
    factory = Property(Any)

    #: Shadow attribute storing the value for the corresponding property.
    _factory = Any

    def _get_factory(self):
        if isinstance(self._factory, basestring):
            self._factory = _import_symbol(self._factory)

        return self._factory

    def _set_factory(self, value):
        self._factory = value

        return

    #: Adapters created by the factory adapt from this protocol.
    #: It can be a string in the form 'foo.bar.baz' which is turned
    #: into an import statement 'from foo.bar import baz' and imported when
    #: this trait is first requested.
    from_protocol = Property(Any)

    #: Shadow attribute storing the value for the corresponding property.
    _from_protocol = Any

    def _get_from_protocol(self):
        if isinstance(self._from_protocol, basestring):
            self._from_protocol = _import_symbol(self._from_protocol)

        return self._from_protocol

    def _set_from_protocol(self, value):
        self._from_protocol = value

        return

    #: Adapters created by the factory adapt to this protocol.
    #: It can be a string in the form 'foo.bar.baz' which is turned
    #: into an import statement 'from foo.bar import baz' and imported when
    #: this trait is first requested.
    to_protocol = Property(Any)

    #: Shadow attribute storing the value for the corresponding property.
    _to_protocol = Any

    def _get_to_protocol(self):
        if isinstance(self._to_protocol, basestring):
            self._to_protocol = _import_symbol(self._to_protocol)

        return self._to_protocol

    def _set_to_protocol(self, value):
        self._to_protocol = value

        return

    def adapt(self, obj, to_protocol):

        if not AdaptationManager.provides_protocol(type(obj), self.from_protocol):
            return None

        if to_protocol is not self.to_protocol:
            return None

        return self.factory(adaptee=obj)

    #### 'object' protocol ####################################################

    def __repr__(self):
        template = "AdapterFactoryOffer: '{from_}' -> '{to}'"

        from_name = getattr(
            self.from_protocol, __name__, str(self.from_protocol)
        )
        to_name = getattr(
            self.to_protocol, __name__, str(self.to_protocol)
        )

        repr = template.format(from_=from_name, to=to_name)

        return repr

#### EOF ######################################################################
