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
""" An adapter factory that caches adapters per instance. """


import weakref

from traits.api import Any, Bool, HasTraits, Property
from traits.util.api import import_symbol


class CachedAdapterFactory(HasTraits):
    """ An adapter factory that caches adapters per instance.

    We provide this class to provide the caching functionality of the
    old traits 'adapts' implementation. However, note that the cache will
    not be cleared unless you take care of cleaning the 'adaptee' trait once
    your adapter are deleted.

    This class will be removed when the 'adapts' function is removed.

    """

    #### 'object' protocol #####################################################

    def __call__(self, adaptee):
        """ The adapter manager uses callables for adapter factories. """

        adapter = self._adapter_cache.get(adaptee, None)
        if adapter is None:
            adapter = self.factory(adaptee)
            self._adapter_cache[adaptee] = adapter

        return adapter

    #### 'CachedAdapterFactory' protocol #######################################

    #: A callable that actually creates the adapters!
    #:
    #: The factory must ba callable that takes exactly one argument which is
    #: the object to be adapted (known as the adaptee), and returns an
    #: adapter from the `from_protocol` to the `to_protocol`.
    #:
    #: The factory can be specified as either a callable, or a string in the
    #: form 'foo.bar.baz' which is turned into an import statement
    #: 'from foo.bar import baz' and imported when the trait is first accessed.
    factory = Property(Any)

    #: True if the cache is empty, otherwise False.
    #:
    #: This method is mostly here to help testing - the framework does not
    #: rely on it for any other purpose.
    is_empty = Property(Bool)
    def _get_is_empty(self):
        return len(self._adapter_cache) == 0

    #### Private protocol ######################################################

    _adapter_cache = Any
    def __adapter_cache_default(self):
        return weakref.WeakKeyDictionary()

    #: Shadow trait for the corresponding property.
    _factory = Any
    _factory_loaded = Bool(False)

    def _get_factory(self):
        """ Trait property getter. """

        if not self._factory_loaded:
            if isinstance(self._factory, basestring):
                self._factory = import_symbol(self._factory)

            self._factory_loaded = True

        return self._factory

    def _set_factory(self, factory):
        """ Trait property setter. """

        self._factory = factory

        return

#### EOF #######################################################################
