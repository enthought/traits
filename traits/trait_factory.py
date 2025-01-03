# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the TraitFactory class and related objects.

A TraitFactory is a class which allows deferred, but cached, creation of
CTrait instances.  The TraitFactory API provides the ``as_ctrait`` method
so that the trait conversion functions can generate CTrait instances in a
standard way.
"""

from .trait_errors import TraitError


_trait_factory_instances = {}


class TraitFactory(object):
    """ A factory class that allows deferred creation of traits

    Traits created by TraitFactory instances are cached, and the cached
    trait is returned by all subsequent calls to the same TraitFactory
    instance.
    """

    def __init__(self, maker_function=None):
        if maker_function is not None:
            self.maker_function = maker_function
            self.__doc__ = maker_function.__doc__

    def __call__(self, *args, **metadata):
        """ Creates a CTrait instance. """
        return self.maker_function(*args, **metadata)

    def as_ctrait(self):
        """ Get the CTrait instance from the factory. """
        return trait_factory(self)


class TraitImportError(TraitFactory):
    """ TraitFactory subclass that always fails when creating a CTrait

    This class is designed for uses such as deferring import problems until
    encountering code that actually tries to use the unimportable trait.
    """

    def __init__(self, message):
        self.message = message

    def __call__(self, *args, **metadata):
        """ Raises an TraitError with the message as is payload. """
        raise TraitError(self.message)


def trait_factory(trait):
    """ Returns a trait created from a TraitFactory instance """
    global _trait_factory_instances

    tid = id(trait)
    if tid not in _trait_factory_instances:
        _trait_factory_instances[tid] = trait()

    return _trait_factory_instances[tid]
