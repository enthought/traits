"""Trivial Interfaces and Adaptation from PyProtocols.

This package is a direct copy of a subset of the files from Phillip J. Eby's
PyProtocols package. They are only included here to help remove dependencies
on external packages from the Traits package. The only significant change is
the inclusion of a setup.py file.
"""

from traits.util.api import deprecated

@deprecated("use the 'adapt' function in 'traits.adaptation' instead")
def adapt(*args, **kw):
    from traits.adaptation.api import adapt

    return adapt(*args, **kw)

@deprecated("use the 'register_factory' function in 'traits.adaptation' instead")
def declareAdapter(factory, provides,
                   forTypes=(), forProtocols=(), forObjects=()):

    from traits.adaptation.api import register_factory
    from itertools import chain

    for from_protocol in chain(forTypes, forProtocols, forObjects):
        for to_protocol in provides:
            register_factory(factory, from_protocol, to_protocol)

@deprecated("use the 'register_provides' function in 'traits.adaptation' instead")
def declareImplementation(protocol,
                          instancesProvide=(), instancesDoNotProvide=()):

    from traits.adaptation.api import register_provides

    for to_protocol in instancesProvide:
        register_provides(protocol, to_protocol)

from traits.adaptation.adaptation_error import AdaptationError \
    as AdaptationFailure

# We will provide decorators as replacements for 'implements' and 'adapts'
# in the future.
from .advice import addClassAdvisor
