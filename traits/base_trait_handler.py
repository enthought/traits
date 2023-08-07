# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Defines the Abstract BaseTraitHandler class.

A trait handler mediates the assignment of values to object traits. It
verifies (via its validate() method) that a specified value is consistent
with the object trait, and generates a TraitError exception if it is not
consistent.
"""

from .constants import DefaultValue
from .trait_errors import TraitError


class BaseTraitHandler(object):
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
    """

    default_value_type = DefaultValue.unspecified
    has_items = False
    is_mapped = False
    editor = None
    info_text = "a legal value"

    def is_valid(self, object, name, value):
        try:
            validate = self.validate
            try:
                validate(object, name, value)
                return True
            except Exception:
                return False
        except Exception:
            return True

    def error(self, object, name, value):
        """Raises a TraitError exception.

        This method is called by the validate() method when an assigned value
        is not valid. Raising a TraitError exception either notifies the user
        of the problem, or, in the case of compound traits, provides a chance
        for another trait handler to handle to validate the value.

        Parameters
        ----------
        object : object
            The object whose attribute is being assigned.
        name : str
            The name of the attribute being assigned.
        value : object
            The proposed new value for the attribute.
        """
        raise TraitError(
            object, name, self.full_info(object, name, value), value
        )

    def full_info(self, object, name, value):
        """Returns a string describing the type of value accepted by the
        trait handler.

        The string should be a phrase describing the type defined by the
        TraitHandler subclass, rather than a complete sentence. For example,
        use the phrase, "a square sprocket" instead of the sentence, "The value
        must be a square sprocket." The value returned by full_info() is
        combined with other information whenever an error occurs and therefore
        makes more sense to the user if the result is a phrase. The full_info()
        method is similar in purpose and use to the **info** attribute of a
        validator function.

        Note that the result can include information specific to the particular
        trait handler instance. If the full_info() method is not overridden,
        the default method returns the value of calling the info() method.

        Parameters
        ----------
        object : object
            The object whose attribute is being assigned.
        name : str
            The name of the attribute being assigned.
        value :
            The proposed new value for the attribute.
        """
        return self.info()

    def info(self):
        """Must return a string describing the type of value accepted by the
        trait handler.

        The string should be a phrase describing the type defined by the
        TraitHandler subclass, rather than a complete sentence. For example,
        use the phrase, "a square sprocket" instead of the sentence, "The value
        must be a square sprocket." The value returned by info() is combined
        with other information whenever an error occurs and therefore makes
        more sense to the user if the result is a phrase. The info() method is
        similar in purpose and use to the **info** attribute of a validator
        function.

        Note that the result can include information specific to the particular
        trait handler instance. If the info() method is not overridden, the
        default method returns the value of the 'info_text' attribute.
        """
        return self.info_text

    def get_editor(self, trait=None):
        """ Returns a trait editor that allows the user to modify the *trait*
        trait.
        This method only needs to be specified if traits defined using this
        trait handler require a non-default trait editor in trait user
        interfaces. The default implementation of this method returns a trait
        editor that allows the user to type an arbitrary string as the value.

        For more information on trait user interfaces, refer to the *Traits UI
        User Guide*.

        Parameters
        ----------
        trait : Trait
            The trait to be edited.
        """
        if self.editor is None:
            self.editor = self.create_editor()

        return self.editor

    def create_editor(self):
        """ Returns the default traits UI editor to use for a trait.
        """
        from traitsui.api import TextEditor

        return TextEditor()

    def inner_traits(self):
        """ Returns a tuple containing the *inner traits* for this trait. Most
            trait handlers do not have any inner traits, and so will return an
            empty tuple. The exceptions are **List** and **Dict** trait types,
            which have inner traits used to validate the values assigned to the
            trait. For example, in *List( Int )*, the *inner traits* for
            **List** are ( **Int**, ).
        """
        return ()
