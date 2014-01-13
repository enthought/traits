#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
#------------------------------------------------------------------------------
""" Base classes for adapters.

Adapters do not have to inherit from these classes, as long as their
constructor takes the object to be adapted as the first and only
*positional* argument.

"""


from traits.has_traits import HasTraits
from traits.trait_types import Any
from traits.util.deprecated import deprecated


class PurePythonAdapter(object):
    """ Base class for pure Python adapters. """

    def __init__(self, adaptee):
        """ Constructor. """

        self.adaptee = adaptee

        return


class Adapter(HasTraits):
    """ Base class for adapters with traits. """

    def __init__(self, adaptee, **traits):
        """ Constructor. """

        traits['adaptee'] = adaptee
        super(Adapter, self).__init__(**traits)

        return

    adaptee = Any


def adapts(from_, to, extra=None, factory=None, cached=False, when=''):
    """ A class advisor for declaring adapters.

    Parameters
    ----------
    from_ : type or interface
        What the adapter adapts *from*, or a list of such types or interfaces
        (the '_' suffix is used because 'from' is a Python keyword).
    to : type or interface
        What the adapter adapts *to*, or a list of such types or interfaces.
    factory : callable
        An (optional) factory for actually creating the adapters. This is
        any callable that takes a single argument which is the object to
        be adapted. The factory should return an adapter if it can
        perform the adaptation and **None** if it cannot.
    cached : bool
        Should the adapters be cached? If an adapter is cached, then the
        factory will produce at most one adapter per instance.
    when : str
        A Python expression that selects which instances of a particular type
        can be adapted by this factory. The expression is evaluated in a
        namespace that contains a single name *adaptee*, which is bound to the
        object to be adapted (e.g., 'adaptee.is_folder').

    Note
    ----
    The ``cached`` and ``when`` arguments are ignored if ``factory`` is
    specified.

    """

    from traits.adaptation.api import register_factory
    from traits.adaptation.cached_adapter_factory import CachedAdapterFactory
    from traits.protocols.advice import addClassAdvisor

    if extra is not None:
        adapter, from_, to = from_, to, extra
    else:
        adapter = None

    @deprecated("use the 'register_factory' function from 'traits.api' instead")
    def callback(klass):
        """ Called when the class has been created. """

        # At this point:-
        #
        # klass is the callable (usually a class) that takes one argument (the
        # adaptee) and returns an appropriate adapter (or None if the adaptation
        # is not possible).

        # What the adapters created by the factory will adapt from.
        if type(from_) is not list:
            from_protocols = [from_]

        else:
            from_protocols = from_

        # What the adapters created by the factory will adapt to.
        if type(to) is not list:
            to_protocols = [to]

        else:
            to_protocols = to

        if factory is None:
            # If the adapter is cached or has a 'when' expression then create a
            # default factory:

            adapter_factory = klass

            if when != '':
                def _conditional_factory(adaptee, *args, **kw):
                    namespace = {'adaptee': adaptee}

                    if eval(when, namespace, namespace):
                        return klass(adaptee, *args, **kw)

                    return None

                adapter_factory = _conditional_factory

            if cached:
                adapter_factory = CachedAdapterFactory(factory=adapter_factory)

        else:
            adapter_factory = factory

        for from_protocol in from_protocols:
            for to_protocol in to_protocols:
                register_factory(adapter_factory, from_protocol, to_protocol)

        for to_protocol in to_protocols:
            # We cannot register adapter factories that are functions. (This is
            # ony relevant when using 'adapts' as a function.
            if isinstance(klass, type):
                # We use type(to_protocol) in case the to_protocols implements
                # its own 'register' method which overrides the ABC method.
                type(to_protocol).register(to_protocol, klass)

        return klass

    if adapter is not None:
        callback(adapter)

    else:
        addClassAdvisor(callback)

#### EOF ######################################################################
