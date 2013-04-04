""" The abstract base class for adapter factories. """


from traits.api import Any, HasTraits, Property

from apptools.adaptation.adapter_manager import AdaptationManager
from apptools.naming.initial_context import _import_symbol


class AdapterOffer(HasTraits):

    #### 'AdapterFactoryOffer' protocol #######################################

    #: A callable that takes as only argument the adaptee and returns
    #: an adapter instance.
    #: It can be a string in the form 'foo.bar.baz' which is turned
    #: into an import statement 'from foo.bar import baz' and imported when
    #: this trait is first requested.
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

        if not AdaptationManager.provides_protocol(type(obj),self.from_protocol):
            return None

        if to_protocol is not self.to_protocol:
            return None

        return self.factory(adaptee=obj)

    #### 'object' protocol ####################################################

    def __repr__(self):
        template = "AdapterFactoryOffer: '{from_}' -> '{to}'"
        repr = template.format(
            from_ = self.from_protocol.__name__,
            to    = self.to_protocol.__name__
        )
        return repr

#### EOF ######################################################################
