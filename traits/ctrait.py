# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the core CTrait class.

The CTrait class extends the C-level cTrait type to provide the full CTrait
API. CTraits are the core objects that are used to generate defaults and
validate as well as maintining a list of notifiers and calling them when
values are modified.
"""

import inspect

from . import ctraits
from .constants import ComparisonMode, DefaultValue, default_value_map
from .observation.i_observable import IObservable
from .trait_base import SequenceTypes, Undefined
from .trait_dict_object import TraitDictObject
from .trait_list_object import TraitListObject
from .trait_set_object import TraitSetObject


def __newobj__(cls, *args):
    """ Unpickles new-style objects.
    """
    return cls.__new__(cls, *args)


@IObservable.register
class CTrait(ctraits.cTrait):
    """ Extends the underlying C-based cTrait type.
    """

    def __call__(self, *args, **metadata):
        """ Allows a derivative trait to be defined from this one. """
        from .trait_type import TraitType
        from .traits import Trait

        handler = self.handler
        if isinstance(handler, TraitType):
            dict = (self.__dict__ or {}).copy()
            dict.update(metadata)

            return handler(*args, **dict)

        metadata.setdefault("parent", self)
        return Trait(*(args + (self,)), **metadata)

    @property
    def default(self):
        kind, value = self.default_value()
        if kind in (
            DefaultValue.object,
            DefaultValue.callable_and_args,
            DefaultValue.callable,
            DefaultValue.disallow,
        ):
            return Undefined
        elif kind in (
            DefaultValue.dict_copy,
            DefaultValue.trait_dict_object,
            DefaultValue.trait_set_object,
            DefaultValue.list_copy,
            DefaultValue.trait_list_object,
        ):
            return value.copy()
        elif kind in {DefaultValue.constant, DefaultValue.missing}:
            return value
        else:
            # This shouldn't ever happen.
            raise RuntimeError(
                "Unexpected default value kind: {!r}".format(kind)
            )

    @property
    def default_kind(self):
        return default_value_map[self.default_value()[0]]

    @property
    def trait_type(self):
        handler = self.handler
        if handler is not None:
            return handler
        else:
            from .trait_types import Any

            return Any

    @property
    def inner_traits(self):
        handler = self.handler
        if handler is not None:
            return handler.inner_traits()

        return ()

    @property
    def comparison_mode(self):
        """ Get or set the comparison mode on the trait.
        Getter returns a ComparisonMode enum.
        Setter acceps either an int or a ComparisonMode enum.
        """
        i_comparison_mode = super().comparison_mode
        return ComparisonMode(i_comparison_mode)

    @comparison_mode.setter
    def comparison_mode(self, value):
        ctraits.cTrait.comparison_mode.__set__(self, value)

    @property
    def property_fields(self):
        """ Return a tuple of callables (fget, fset, validate) for the
        property trait."""
        return self._get_property()

    @property_fields.setter
    def property_fields(self, value):
        """ Set the fget, fset, validate callables for the property.

        Parameters
        ----------
        value : tuple
            Value should be the tuple of callables (fget, fset, validate).

        """
        func_arg_counts = []

        for arg in value:

            if arg is None:
                nargs = 0
            else:
                sig = inspect.signature(arg)
                nargs = len(sig.parameters)

            func_arg_counts.extend([arg, nargs])

        self._set_property(*func_arg_counts)

    def is_trait_type(self, trait_type):
        """ Returns whether or not this trait is of a specified trait type.
        """
        return isinstance(self.trait_type, trait_type)

    def get_editor(self):
        """ Returns the user interface editor associated with the trait.
        """
        from traitsui.api import EditorFactory

        # See if we have an editor:
        editor = self.editor
        if editor is None:

            # Else see if the trait handler has an editor:
            handler = self.handler
            if handler is not None:
                editor = handler.get_editor(self)

            # If not, give up and use a default text editor:
            if editor is None:
                from traitsui.api import TextEditor

                editor = TextEditor

        # If the result is not an EditorFactory:
        if not isinstance(editor, EditorFactory):
            # Then it should be a factory for creating them:
            args = ()
            traits = {}
            if type(editor) in SequenceTypes:
                for item in editor[:]:
                    if type(item) in SequenceTypes:
                        args = tuple(item)
                    elif isinstance(item, dict):
                        traits = item
                        if traits.get("trait", 0) is None:
                            traits = traits.copy()
                            traits["trait"] = self
                    else:
                        editor = item
            editor = editor(*args, **traits)

        # Cache the result:
        self.editor = editor

        # Return the resulting EditorFactory object:
        return editor

    def get_help(self, full=True):
        """ Returns the help text for a trait.

        If *full* is False or the trait does not have a **help** string,
        the returned string is constructed from the **desc** attribute on the
        trait and the **info** string on the trait's handler.

        Parameters
        ----------
        full : bool
            Indicates whether to return the value of the *help* attribute of
            the trait itself.
        """
        if full:
            help = self.help
            if help is not None:
                return help

        handler = self.handler
        if handler is not None:
            info = "must be %s." % handler.info()
        else:
            info = "may be any value."

        desc = self.desc
        if self.desc is None:
            return info.capitalize()

        return "Specifies %s and %s" % (desc, info)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        handler = self.handler
        if handler is not None:
            return handler.full_info(object, name, value)

        return "any value"

    def info(self):
        """ Returns a description of the trait.
        """
        handler = self.handler
        if handler is not None:
            return handler.info()

        return "any value"

    def as_ctrait(self):
        """ Method that returns self for trait converters. """
        return self

    def __reduce_ex__(self, protocol):
        """ Returns the pickleable form of a CTrait object. """
        return (__newobj__, (self.__class__, 0), self.__getstate__())


def _adapt_wrapper(*args, **kw):
    # We need this wrapper to defer the import of 'adapt' and avoid a circular
    # import. The ctraits 'adapt' callback needs to be set as soon as possible,
    # but the adaptation mechanism relies on traits.

    # This wrapper is called once, after which we set the ctraits callback
    # to point directly to 'adapt'.

    from traits.adaptation.api import adapt

    ctraits._adapt(adapt)
    return adapt(*args, **kw)


# Make sure the Python-level version of the trait class is known to all
# interested parties:

ctraits._ctrait(CTrait)

#: Register Trait container object classes with ctraits.c
ctraits._list_classes(TraitListObject, TraitSetObject, TraitDictObject)

#: Tell the C-based traits module about the traits adaptation 'adapt' function
ctraits._adapt(_adapt_wrapper)
