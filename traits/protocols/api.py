"""Trivial Interfaces and Adaptation from PyProtocols.

This package is a direct copy of a subset of the files from Phillip J. Eby's
PyProtocols package. They are only included here to help remove dependencies
on external packages from the Traits package. The only significant change is
the inclusion of a setup.py file.
"""

from traits.util.api import deprecated

@deprecated("use the 'adapt' function in 'traits.adaptation' instead")
def adapt(*args, **kw):
    from apptools.adaptation.api import adapt

    return adapt(*args, **kw)

@deprecated("use the 'register_factory' function in 'traits.adaptation' instead")
def declareAdapter(factory, provides,
                   forTypes=(), forProtocols=(), forObjects=()):

    from apptools.adaptation.api import register_factory
    from itertools import chain

    for from_protocol in chain(forTypes, forProtocols, forObjects):
        for to_protocol in provides:
            register_factory(factory, from_protocol, to_protocol)

@deprecated("use ABC's 'register method, or declare a null adapter instead")
def declareImplementation(protocol,
                          instancesProvide=(), instancesDoNotProvide=()):

    from apptools.adaptation.api import register_factory

    def null_adapter(adaptee):
        return adaptee

    for to_protocol in instancesProvide:
        register_factory(null_adapter, protocol, to_protocol)

from apptools.adaptation.adaptation_error import AdaptationError \
    as AdaptationFailure

AdaptationFailure = deprecated(
    "use 'AdaptationError' in 'traits.adaptation' instead"
)(AdaptationFailure)

# We will provide decorators as replacements for 'implements' and 'adapts'
# in the future.
from .advice import addClassAdvisor
