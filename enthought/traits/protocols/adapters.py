"""Basic Adapters and Adapter Operations"""

__all__ = [
    'NO_ADAPTER_NEEDED','DOES_NOT_SUPPORT', 'Adapter',
    'minimumAdapter', 'composeAdapters', 'updateWithSimplestAdapter',
    'StickyAdapter', 'AdaptationFailure', 'bindAdapter',
]

from types \
    import FunctionType,ClassType,MethodType

try:
    PendingDeprecationWarning
except NameError:
    class PendingDeprecationWarning(Warning):
        'Base class for warnings about features which will be deprecated in the future.'

class AdaptationFailure(NotImplementedError,TypeError):
    """A suitable implementation/adapter could not be found"""

# Fundamental Adapters

def NO_ADAPTER_NEEDED(obj, protocol=None):
    """Assume 'obj' implements 'protocol' directly"""
    return obj

def DOES_NOT_SUPPORT(obj, protocol=None):
    """Prevent 'obj' from supporting 'protocol'"""
    return None


try:
    from _speedups import NO_ADAPTER_NEEDED, DOES_NOT_SUPPORT
except ImportError:
    pass

    
def _getProto(self):
    from warnings import warn
    warn("The 'protocol' attribute of Adapter subclass %s is being used"
        % (self.__class__,), DeprecationWarning, 2)
    return self.__dict__['protocol']

def _setProto(self,proto):
    self.__dict__['protocol'] = proto


class Adapter(object):
    """Convenient base class for adapters"""

    protocol = property(_getProto,_setProto)

    def __init__(self, ob, proto):
        self.subject = ob
        self.protocol = proto


class StickyAdapter(object):
    """Adapter that attaches itself to its subject for repeated use"""

    attachForProtocols = ()
    protocol = property(_getProto,_setProto)

    def __init__(self, ob, proto):
        self.subject = ob
        self.protocol = proto

        # Declare this instance as a per-instance adaptation for the
        # given protocol

        provides = list(self.attachForProtocols)
        if proto is not None and proto not in provides:
            provides.append(proto)

        from protocols.api import declareAdapter
        declareAdapter(lambda s: self, provides, forObjects=[ob])


# Adapter "arithmetic"

def minimumAdapter(a1,a2,d1=0,d2=0):

    """Shortest route to implementation, 'a1' @ depth 'd1', or 'a2' @ 'd2'?

    Assuming both a1 and a2 are interchangeable adapters (i.e. have the same
    source and destination protocols), return the one which is preferable; that
    is, the one with the shortest implication depth, or, if the depths are
    equal, then the adapter that is composed of the fewest chained adapters.
    If both are the same, then prefer 'NO_ADAPTER_NEEDED', followed by
    anything but 'DOES_NOT_SUPPORT', with 'DOES_NOT_SUPPORT' being least
    preferable.  If there is no unambiguous choice, and 'not a1 is a2',
    TypeError is raised.
    """

    if d1<d2:
        return a1
    elif d2<d1:
        return a2

    if getattr(a1,'__unbound_adapter__',a1) is getattr(a2,'__unbound_adapter__',a2):
        return a1   # don't care which

    a1ct = getattr(a1,'__adapterCount__',1)
    a2ct = getattr(a2,'__adapterCount__',1)

    if a1ct<a2ct:
        return a1
    elif a2ct<a1ct:
        return a2

    if a1 is NO_ADAPTER_NEEDED or a2 is DOES_NOT_SUPPORT:
        return a1

    if a1 is DOES_NOT_SUPPORT or a2 is NO_ADAPTER_NEEDED:
        return a2

    # it's ambiguous
    raise TypeError("Ambiguous adapter choice", a1, a2, d1, d2)

def composeAdapters(baseAdapter, baseProtocol, extendingAdapter):

    """Return the composition of 'baseAdapter'+'extendingAdapter'"""

    if baseAdapter is DOES_NOT_SUPPORT or extendingAdapter is DOES_NOT_SUPPORT:
        # fuhgeddaboudit
        return DOES_NOT_SUPPORT

    if baseAdapter is NO_ADAPTER_NEEDED:
        return extendingAdapter

    if extendingAdapter is NO_ADAPTER_NEEDED:
        return baseAdapter

    def newAdapter(ob):
        ob = baseAdapter(ob)
        if ob is not None:
            return extendingAdapter(ob)

    newAdapter.__adapterCount__ = (
        getattr(extendingAdapter,'__adapterCount__',1)+
        getattr(baseAdapter,'__adapterCount__',1)
    )

    return newAdapter


def bindAdapter(adapter,proto):
    """Backward compatibility: wrap 'adapter' to support old 2-arg signature"""

    maxargs = 2; f = adapter; tries = 10

    while not isinstance(f,FunctionType) and tries:
        if isinstance(f,MethodType):
            maxargs += (f.im_self is not None)
            f = f.im_func
            tries = 10
        elif isinstance(f,(ClassType,type)):
            maxargs += 1
            f = f.__init__
            tries -=1
        else:
            f = f.__call__
            tries -=1

    if isinstance(f,FunctionType):

        from inspect import getargspec
        args, varargs, varkw, defaults = getargspec(f)

        if defaults:
            args = args[:-len(defaults)]

        if len(args)>=maxargs:
            newAdapter = lambda ob: adapter(ob,proto)
            newAdapter.__adapterCount__ = getattr(
                adapter,'__adapterCount__',1
            )
            newAdapter.__unbound_adapter__ = adapter
            if f not in (Adapter.__init__.im_func, StickyAdapter.__init__.im_func):
                from warnings import warn
                warn("Adapter %r to protocol %r needs multiple arguments"
                    % (adapter,proto), PendingDeprecationWarning, 6)
            return newAdapter

    return adapter


def updateWithSimplestAdapter(mapping, key, adapter, depth):

    """Replace 'mapping[key]' w/'adapter' @ 'depth', return true if changed"""

    new = adapter
    old = mapping.get(key)

    if old is not None:
        old, oldDepth = old
        new = minimumAdapter(old,adapter,oldDepth,depth)
        if old is new and depth>=oldDepth:
            return False

    mapping[key] = new, depth
    return True

