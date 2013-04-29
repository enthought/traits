""" An offer to provide adapters from one protocol to another. """


from traits.api import Any, Bool, HasTraits, Property

from apptools.adaptation.adaptation_manager import AdaptationManager
from apptools.naming.initial_context import _import_symbol


class AdaptationOffer(HasTraits):
    """ An offer to provide adapters from one protocol to another.

    An adaptation offer consists of a factory that can create adapters, and the
    protocols that define what the adapters adapt from and to.

    """

    #### 'object' protocol ####################################################

    def __repr__(self):
        """ Return a string representation of the object. """

        template = "AdaptationOffer: '{from_}' -> '{to}'"

        from_name = getattr(
            self._from_protocol, '__name__', str(self._from_protocol)
        )

        to_name = getattr(
            self._to_protocol, '__name__', str(self._to_protocol)
        )

        return template.format(from_=from_name, to=to_name)

    #### 'AdaptationOffer' protocol ###########################################

    #: A factory for creating adapters.
    #:
    #: The factory must ba callable that takes exactly one argument which is
    #: the object to be adapted (known as the adaptee), and returns an
    #: adapter from the `from_protocol` to the `to_protocol`.
    #:
    #: The factory can be specified as either a callable, or a string in the
    #: form 'foo.bar.baz' which is turned into an import statement
    #: 'from foo.bar import baz' and imported when the trait is first accessed.
    factory = Property(Any)

    #: Adapters created by the factory adapt *from* this protocol.
    #:
    #: The protocol can be specified as a protocol (class/Interface), or a
    #: string in the form 'foo.bar.baz' which is turned into an import
    #: statement 'from foo.bar import baz' and imported when the trait is
    #: accessed.
    from_protocol = Property(Any)
    from_protocol_name = Property(Any)
    def _get_from_protocol_name(self):
        return self._get_type_name(self._from_protocol)

    #: Adapters created by the factory adapt *to* this protocol.
    #:
    #: The protocol can be specified as a protocol (class/Interface), or a
    #: string in the form 'foo.bar.baz' which is turned into an import
    #: statement 'from foo.bar import baz' and imported when the trait is
    #: accessed.
    to_protocol = Property(Any)

    #### Private protocol ######################################################

    #: Shadow trait for the corresponding property.
    _factory = Any
    _factory_loaded = Bool(False)

    def _get_factory(self):
        """ Trait property getter. """

        if not self._factory_loaded:
            if isinstance(self._factory, basestring):
                self._factory = _import_symbol(self._factory)

            self._factory_loaded = True

        return self._factory

    def _set_factory(self, factory):
        """ Trait property setter. """

        self._factory = factory

        return

    #: Shadow trait for the corresponding property.
    _from_protocol = Any
    _from_protocol_loaded = Bool(False)

    def _get_from_protocol(self):
        """ Trait property getter. """

        if not self._from_protocol_loaded:
            if isinstance(self._from_protocol, basestring):
                self._from_protocol = _import_symbol(self._from_protocol)

            self._from_protocol_loaded = True

        return self._from_protocol

    def _set_from_protocol(self, from_protocol):
        """ Trait property setter. """

        self._from_protocol = from_protocol

        return

    #: Shadow trait for the corresponding property.
    _to_protocol = Any
    _to_protocol_loaded = Bool(False)

    def _get_to_protocol(self):
        """ Trait property getter. """

        if not self._to_protocol_loaded:
            if isinstance(self._to_protocol, basestring):
                self._to_protocol = _import_symbol(self._to_protocol)

            self._to_protocol_loaded = True

        return self._to_protocol

    def _set_to_protocol(self, to_protocol):
        """ Trait property setter. """

        self._to_protocol = to_protocol

        return

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

#### EOF ######################################################################
