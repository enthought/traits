#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

""" Defines the abstract EditorFactory class, which represents a factory for
    creating the Editor objects used in a Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

import sys, os

from ..api import HasPrivateTraits, Callable, Str, Bool, Event, Any, Property

from .helper import enum_values_changed

from .toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'EditorFactory' abstract base class:
#-------------------------------------------------------------------------------

class EditorFactory ( HasPrivateTraits ):
    """ Represents a factory for creating the Editor objects in a Traits-based
        user interface.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Function to use for string formatting
    format_func = Callable

    # Format string to use for formatting (used if **format_func** is not set).
    format_str = Str

    # Is the editor being used to create table grid cells?
    is_grid_cell = Bool( False )

    # Are created editors initially enabled?
    enabled = Bool( True )

    # The extended trait name of the trait containing editor invalid state
    # status:
    invalid = Str

    # The editor class to use for 'simple' style views.
    simple_editor_class = Property

    # The editor class to use for 'custom' style views.
    custom_editor_class = Property

    # The editor class to use for 'text' style views.
    text_editor_class   = Property

    # The editor class to use for 'readonly' style views.
    readonly_editor_class = Property

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *args, **traits ):
        """ Initializes the factory object.
        """
        HasPrivateTraits.__init__( self, **traits )
        self.init( *args )

    #---------------------------------------------------------------------------
    #  Performs any initialization needed after all constructor traits have
    #  been set:
    #---------------------------------------------------------------------------

    def init ( self ):
        """ Performs any initialization needed after all constructor traits
            have been set.
        """
        pass

    #---------------------------------------------------------------------------
    #  Returns the value of a specified extended name of the form: name or
    #  context_object_name.name[.name...]:
    #---------------------------------------------------------------------------

    def named_value ( self, name, ui ):
        """ Returns the value of a specified extended name of the form: name or
            context_object_name.name[.name...]:
        """
        names = name.split( '.' )

        if len( names ) == 1:
            # fixme: This will produce incorrect values if the actual Item the
            # factory is being used with does not use the default object='name'
            # value, and the specified 'name' does not contain a '.'. The
            # solution will probably involve providing the Item as an argument,
            # but it is currently not available at the time this method needs to
            # be called...
            names.insert( 0, 'object' )

        value = ui.context[ names[0] ]
        for name in names[1:]:
            value = getattr( value, name )

        return value
    #---------------------------------------------------------------------------
    #  Methods that generate backend toolkit-specific editors.
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "simple" style.
        """
        return self.simple_editor_class( parent,
                                         factory     = self,
                                         ui          = ui,
                                         object      = object,
                                         name        = name,
                                         description = description )

    def custom_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "custom" style.
        """
        return self.custom_editor_class( parent,
                                         factory     = self,
                                         ui          = ui,
                                         object      = object,
                                         name        = name,
                                         description = description )

    def text_editor ( self, ui, object, name, description, parent ):
        """ Generates an editor using the "text" style.
        """
        return self.text_editor_class( parent,
                                       factory     = self,
                                       ui          = ui,
                                       object      = object,
                                       name        = name,
                                       description = description )

    def readonly_editor ( self, ui, object, name, description, parent ):
        """ Generates an "editor" that is read-only.
        """
        return self.readonly_editor_class( parent,
                                           factory     = self,
                                           ui          = ui,
                                           object      = object,
                                           name        = name,
                                           description = description )

    #---------------------------------------------------------------------------
    #  Private methods
    #---------------------------------------------------------------------------
    @classmethod
    def _get_toolkit_editor(cls, class_name):
        """
        Returns the editor by name class_name in the backend package.
        """
        editor_factory_classes = [factory_class for factory_class in cls.mro()
                                  if issubclass(factory_class, EditorFactory)]
        for index in range(len( editor_factory_classes )):
            try:
                factory_class = editor_factory_classes[index]
                editor_file_name = os.path.basename(
                                sys.modules[factory_class.__module__].__file__)
                return toolkit_object(':'.join([editor_file_name.split('.')[0],
                                             class_name]), True)
            except Exception, e:
                if index == len(editor_factory_classes)-1:
                    raise e
        return None

    #---------------------------------------------------------------------------
    #  Property getters
    #---------------------------------------------------------------------------

    def _get_simple_editor_class(self):
        """ Returns the editor class to use for "simple" style views.
        The default implementation tries to import the SimpleEditor class in the
        editor file in the backend package, and if such a class is not to found
        it returns the SimpleEditor class defined in editor_factory module in
        the backend package.

        """
        try:
            SimpleEditor = self._get_toolkit_editor('SimpleEditor')
        except:
            SimpleEditor = toolkit_object('editor_factory:SimpleEditor')
        return SimpleEditor


    def _get_custom_editor_class(self):
        """ Returns the editor class to use for "custom" style views.
        The default implementation tries to import the CustomEditor class in the
        editor file in the backend package, and if such a class is not to found
        it returns simple_editor_class.

        """
        try:
            CustomEditor = self._get_toolkit_editor('CustomEditor')
        except:
            CustomEditor = self.simple_editor_class
        return CustomEditor


    def _get_text_editor_class(self):
        """ Returns the editor class to use for "text" style views.
        The default implementation tries to import the TextEditor class in the
        editor file in the backend package, and if such a class is not found
        it returns the TextEditor class declared in the editor_factory module in
        the backend package.

        """
        try:
            TextEditor = self._get_toolkit_editor('TextEditor')
        except:
            TextEditor = toolkit_object('editor_factory:TextEditor')
        return TextEditor


    def _get_readonly_editor_class(self):
        """ Returns the editor class to use for "readonly" style views.
        The default implementation tries to import the ReadonlyEditor class in
        the editor file in the backend package, and if such a class is not found
        it returns the ReadonlyEditor class declared in the editor_factory
        module in the backend package.

        """
        try:
            ReadonlyEditor = self._get_toolkit_editor('ReadonlyEditor')
        except:
            ReadonlyEditor = toolkit_object('editor_factory:ReadonlyEditor')
        return ReadonlyEditor


#-------------------------------------------------------------------------------
#  'EditorWithListFactory' abstract base class:
#-------------------------------------------------------------------------------

class EditorWithListFactory ( EditorFactory ):
    """ Base class for factories of editors for objects that contain lists.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Values to enumerate (can be a list, tuple, dict, or a CTrait or
    # TraitHandler that is "mapped"):
    values = Any

    # Extended name of the trait on **object** containing the enumeration data:
    object = Str( 'object' )

    # Name of the trait on 'object' containing the enumeration data
    name = Str

    # Fired when the **values** trait has been updated:
    values_modified = Event

    #---------------------------------------------------------------------------
    #  Recomputes the mappings whenever the 'values' trait is changed:
    #---------------------------------------------------------------------------

    def _values_changed ( self ):
        """ Recomputes the mappings whenever the **values** trait is changed.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed( self.values )

        self.values_modified = True

## EOF ########################################################################
