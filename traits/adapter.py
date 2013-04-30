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

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

# Standard library imports:
import weakref

# Traits imports:
from .has_traits import HasTraits
from .trait_types import Any, Bool, Expression

# PyProtocols imports:
from .protocols.advice import addClassAdvisor

#-------------------------------------------------------------------------------
#  'Adapter' class:
#-------------------------------------------------------------------------------

class Adapter ( HasTraits ):
    """ The base class for all traits adapters.

    In Traits, an *adapter* is a special type of class whose role is to
    transform some type of object which does not implement a specific interface,
    or set of interfaces, into one that does.

    This class is provided as a convenience. If you subclass this class, the
    only things you need to add to the subclass definition are:

        * An implements() function call declaring which interfaces the adapter
          class implements on behalf of the object is is adapting.
        * A declaration for the **adaptee** trait, usually as an Instance of
          a particular class.
        * The actual implementations of the interfaces declared in the
          implements() call. Usually the implementation code is written in
          terms of the **adaptee** trait.

    """

    #-- Trait Definitions ------------------------------------------------------

    #: The object that is being adapted.
    adaptee = Any

    #-- Constructor ------------------------------------------------------------

    def __init__ ( self, adaptee ):
        """ Constructor.

            We have to declare an explicit constructor because adapters are
            created by PyProtocols itself, which knows nothing about traits.
        """
        super( Adapter, self ).__init__()

        self.adaptee = adaptee

#-------------------------------------------------------------------------------
#  'DefaultAdapterFactory' class:
#-------------------------------------------------------------------------------

class DefaultAdapterFactory ( HasTraits ):
    """ An adapter factory for producing cached or categorized adapters.
    """

    #-- 'DefaultAdapterFactory' Interface --------------------------------------

    #: The adapter class that this factory creates instances of
    klass = Any

    #: Does the factory generate cached adapters?
    #: If an adapter is cached then the factory will produce at most one
    #: adapter per instance.
    cached = Bool( False )

    #: An expression that is used to select which instances of a particular
    #: type can be adapted by this factory.
    #:
    #: The expression is evaluated in a namespace that contains a single name
    #: 'adaptee', which is bound to the object that this factory is attempting
    #: to adapt (e.g. 'adaptee.is_folder').
    when = Expression

    #-- Private Interface ------------------------------------------------------

    # If this is a cached adapter factory, then this mapping will contain
    # the adapters keyed by weak references to the adapted objects.
    _adapters = Any

    #---------------------------------------------------------------------------
    #  'IAdapterFactory' interface:
    #---------------------------------------------------------------------------

    def __call__ ( self, object ):
        """ Creates an adapter for the specified object.

            Returns **None** if the factory cannot perform the required
            adaptation.
        """
        namespace = { 'adaptee': object }
        if eval( self.when_, namespace, namespace ):
            if self.cached:
                adapter = self._adapters.get( object )
                if adapter is None:
                    self._adapters[ object ] = adapter = self.klass( object )

                return adapter

            return self.klass( object )

        return None

    #---------------------------------------------------------------------------
    #  Private interface:
    #---------------------------------------------------------------------------

    def __adapters_default ( self ):
        """ Trait initializer.
        """
        return weakref.WeakKeyDictionary()

#-------------------------------------------------------------------------------
#  'adapts' function:
#-------------------------------------------------------------------------------

def adapts ( from_, to, extra = None, factory = None, cached = False,
                        when  = '' ):
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
            if cached or (when != ''):
                adapter_factory = DefaultAdapterFactory(
                    klass=klass, cached=cached, when=when or 'True'
                )

            # Otherwise, just use the adapter class itself.
            else:
                adapter_factory = klass

        else:
            adapter_factory = factory

        for from_protocol in from_protocols:
            for to_protocol in to_protocols:
                register_factory(adapter_factory, from_protocol, to_protocol)

        return klass

    if adapter is not None:
        callback(adapter)

    else:
        addClassAdvisor(callback)

#### EOF ######################################################################
