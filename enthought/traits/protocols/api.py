"""Adapter and Declaration API"""

__all__ = [
    'adapt', 'declareAdapterForType', 'declareAdapterForProtocol',
    'declareAdapterForObject', 'advise', 'declareImplementation',
    'declareAdapter', 'adviseObject',
]

_marker = object()

from sys \
    import _getframe, exc_info, modules

from types \
    import ClassType
    
ClassTypes = ( ClassType, type )

from adapters \
    import NO_ADAPTER_NEEDED, DOES_NOT_SUPPORT, AdaptationFailure
    
from adapters \
    import bindAdapter
    
from advice \
    import addClassAdvisor, getFrameInfo
    
from interfaces \
    import IOpenProtocol, IOpenProvider, IOpenImplementor, Protocol, \
           InterfaceClass, Interface


def adapt(obj, protocol, default=_marker, factory=_marker):

    """PEP 246-alike: Adapt 'obj' to 'protocol', return 'default'

    If 'default' is not supplied and no implementation is found,
    the result of 'factory(obj,protocol)' is returned.  If 'factory'
    is also not supplied, 'NotImplementedError' is then raised."""

    if isinstance(protocol,ClassTypes) and isinstance(obj,protocol):
        return obj

    try:
        _conform = obj.__conform__
    except AttributeError:
        pass
    else:
        try:
            result = _conform(protocol)
            if result is not None:
                return result
        except TypeError:
            if exc_info()[2].tb_next is not None:
                raise

    try:
        _adapt = protocol.__adapt__
    except AttributeError:
        pass
    else:
        try:
            result = _adapt(obj)
            if result is not None:
                return result
        except TypeError:
            if exc_info()[2].tb_next is not None:
                raise

    if default is _marker:
        if factory is not _marker:
            from warnings import warn
            warn("The 'factory' argument to 'adapt()' will be removed in 1.0",
                DeprecationWarning, 2)
            return factory(obj, protocol)

        raise AdaptationFailure("Can't adapt", obj, protocol)

    return default

try:
    from _speedups import adapt
except ImportError:
    pass


# Fundamental, explicit interface/adapter declaration API:
#   All declarations should end up passing through these three routines.

def declareAdapterForType(protocol, adapter, typ, depth=1):
    """Declare that 'adapter' adapts instances of 'typ' to 'protocol'"""
    adapter = bindAdapter(adapter,protocol)
    adapter = adapt(protocol, IOpenProtocol).registerImplementation(
        typ, adapter, depth
    )

    oi = adapt(typ, IOpenImplementor, None)

    if oi is not None:
        oi.declareClassImplements(protocol,adapter,depth)


def declareAdapterForProtocol(protocol, adapter, proto, depth=1):
    """Declare that 'adapter' adapts 'proto' to 'protocol'"""
    adapt(protocol, IOpenProtocol)  # src and dest must support IOpenProtocol
    adapt(proto, IOpenProtocol).addImpliedProtocol(protocol, bindAdapter(adapter,protocol), depth)


def declareAdapterForObject(protocol, adapter, ob, depth=1):
    """Declare that 'adapter' adapts 'ob' to 'protocol'"""
    adapt(protocol,IOpenProtocol).registerObject(ob,bindAdapter(adapter,protocol),depth)

# Bootstrap APIs to work with Protocol and InterfaceClass, without needing to
# give Protocol a '__conform__' method that's hardwired to IOpenProtocol.
# Note that InterfaceClass has to be registered first, so that when the
# registration propagates to IAdaptingProtocol and IProtocol, InterfaceClass
# will already be recognized as an IOpenProtocol, preventing infinite regress.

IOpenProtocol.registerImplementation(InterfaceClass)    # VERY BAD!!
IOpenProtocol.registerImplementation(Protocol)          # NEVER DO THIS!!
# From this line forward, the declaration APIs can work.  Use them instead!

# Interface and adapter declarations - convenience forms, explicit targets

def declareAdapter(factory, provides,
    forTypes=(),
    forProtocols=(),
    forObjects=()
):
    """'factory' is an IAdapterFactory providing 'provides' protocols"""

    for protocol in provides:

        for typ in forTypes:
            declareAdapterForType(protocol, factory, typ)

        for proto in forProtocols:
            declareAdapterForProtocol(protocol, factory, proto)

        for ob in forObjects:
            declareAdapterForObject(protocol, factory, ob)


def declareImplementation(typ, instancesProvide=(), instancesDoNotProvide=()):
    """Declare information about a class, type, or 'IOpenImplementor'"""

    for proto in instancesProvide:
        declareAdapterForType(proto, NO_ADAPTER_NEEDED, typ)

    for proto in instancesDoNotProvide:
        declareAdapterForType(proto, DOES_NOT_SUPPORT, typ)


def adviseObject(ob, provides=(), doesNotProvide=()):
    """Tell an object what it does or doesn't provide"""

    for proto in provides:
        declareAdapterForObject(proto, NO_ADAPTER_NEEDED, ob)

    for proto in doesNotProvide:
        declareAdapterForObject(proto, DOES_NOT_SUPPORT, ob)


# And now for the magic function...

def advise(**kw):
    kw = kw.copy()
    frame = _getframe(1)
    kind, module, caller_locals, caller_globals = getFrameInfo(frame)

    if kind=="module":
        moduleProvides = kw.setdefault('moduleProvides',())
        del kw['moduleProvides']

        for k in kw:
            raise TypeError(
                "Invalid keyword argument for advising modules: %s" % k
            )

        adviseObject(module,
            provides=moduleProvides
        )
        return

    elif kind!="class":
        raise SyntaxError(
            "protocols.advise() must be called directly in a class or"
            " module body, not in a function or exec."
        )

    classProvides         = kw.setdefault('classProvides',())
    classDoesNotProvide   = kw.setdefault('classDoesNotProvide',())
    instancesProvide      = kw.setdefault('instancesProvide',())
    instancesDoNotProvide = kw.setdefault('instancesDoNotProvide',())
    asAdapterForTypes     = kw.setdefault('asAdapterForTypes',())
    asAdapterForProtocols = kw.setdefault('asAdapterForProtocols',())
    protocolExtends       = kw.setdefault('protocolExtends',())
    protocolIsSubsetOf    = kw.setdefault('protocolIsSubsetOf',())
    factoryMethod         = kw.setdefault('factoryMethod',None)
    equivalentProtocols   = kw.setdefault('equivalentProtocols',())

    map(kw.__delitem__,"classProvides classDoesNotProvide instancesProvide"
        " instancesDoNotProvide asAdapterForTypes asAdapterForProtocols"
        " protocolExtends protocolIsSubsetOf factoryMethod equivalentProtocols"
        .split())

    for k in kw:
        raise TypeError(
            "Invalid keyword argument for advising classes: %s" % k
        )

    def callback(klass):
        if classProvides or classDoesNotProvide:
            adviseObject(klass,
                provides=classProvides, doesNotProvide=classDoesNotProvide
            )

        if instancesProvide or instancesDoNotProvide:
            declareImplementation(klass,
                instancesProvide=instancesProvide,
                instancesDoNotProvide=instancesDoNotProvide
            )

        if asAdapterForTypes or asAdapterForProtocols:
            if not instancesProvide:
                raise TypeError(
                    "When declaring an adapter, you must specify what"
                    " its instances will provide."
                )
            if factoryMethod:
                factory = getattr(klass,factoryMethod)
            else:
                factory = klass

            declareAdapter(factory, instancesProvide,
                forTypes=asAdapterForTypes, forProtocols=asAdapterForProtocols
            )
        elif factoryMethod:
            raise TypeError(
                "'factoryMethod' is only used when declaring an adapter type"
            )

        if protocolExtends:
            declareAdapter(NO_ADAPTER_NEEDED, protocolExtends,
                forProtocols=[klass]
            )

        if protocolIsSubsetOf:
            declareAdapter(NO_ADAPTER_NEEDED, [klass],
                forProtocols=protocolIsSubsetOf
            )

        if equivalentProtocols:
            declareAdapter(
                NO_ADAPTER_NEEDED, equivalentProtocols, forProtocols=[klass]
            )
            declareAdapter(
                NO_ADAPTER_NEEDED, [klass], forProtocols=equivalentProtocols
            )

        return klass

    addClassAdvisor(callback)

