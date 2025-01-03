# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Defines the TraitHandler class.

A trait handler mediates the assignment of values to object traits. It
verifies (via its validate() method) that a specified value is consistent
with the object trait, and generates a TraitError exception if it is not
consistent.
"""


from .base_trait_handler import BaseTraitHandler
from .trait_base import class_of
from .trait_errors import TraitError


class TraitHandler(BaseTraitHandler):
    """ The task of this class and its subclasses is to verify the correctness
    of values assigned to object trait attributes.

    This class is an alternative to trait validator functions. A trait handler
    has several advantages over a trait validator function, due to being an
    object:

    * Trait handlers have constructors and state. Therefore, you can use
      them to create *parametrized types*.
    * Trait handlers can have multiple methods, whereas validator functions
      can have only one callable interface. This feature allows more
      flexibility in their implementation, and allows them to handle a
      wider range of cases, such as interactions with other components.

    The only method of TraitHandler that *must* be implemented by subclasses
    is validate().
    """

    def validate(self, object, name, value):
        """ Verifies whether a new value assigned to a trait attribute is
        valid.

        This method *must* be implemented by subclasses of TraitHandler. It is
        called whenever a new value is assigned to a trait attribute defined
        using this trait handler.

        If the value received by validate() is not valid for the trait
        attribute, the method must called the predefined error() method to
        raise a TraitError exception

        Parameters
        ----------
        object : HasTraits instance
            The object whose attribute is being assigned.
        name : str
            The name of the attribute being assigned.
        value : any
            The proposed new value for the attribute.

        Returns
        -------
        any
            If the new value is valid, this method must return either the
            original value passed to it, or an alternate value to be assigned
            in place of the original value. Whatever value this method returns
            is the actual value assigned to *object.name*.

        """
        raise TraitError(
            "The '%s' trait of %s instance has an unknown type. "
            "Contact the developer to correct the problem."
            % (name, class_of(object))
        )
