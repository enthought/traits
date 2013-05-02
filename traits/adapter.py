#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Martin Chilvers
#  Date:   07/18/2007
#
#-------------------------------------------------------------------------------

""" An extension to PyProtocols to simplify the declaration of adapters.
"""


from __future__ import absolute_import


import traits.adaptation.adapter
from .util.deprecated import deprecated


class Adapter(traits.adaptation.adapter.Adapter):

    @deprecated("use 'Adapter' in 'traits.api' instead")
    def __init__(self, adaptee, **traits):
        super(Adapter, self).__init__(adaptee, **traits)


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

    from traits.adaptation.api import CachedAdapterFactory, register_factory
    from traits.protocols.advice import addClassAdvisor

    if extra is not None:
        adapter, from_, to = from_, to, extra
    else:
        adapter = None

    def callback ( klass ):
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

        # fixme: this relies on the protocol being an ABC (which includes
        # traits Interfaces).
        for to_protocol in to_protocols:
            to_protocol.register(klass)

        return klass

    if adapter is not None:
        callback(adapter)

    else:
        addClassAdvisor(callback)

#### EOF ######################################################################
