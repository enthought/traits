#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------
""" Defines the list editor factory for the traits user interface toolkits..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import (HasTraits, BaseTraitHandler, Range, Str, Any, Int, Instance,
        Property, Bool, Callable, Enum, PrototypedFrom)

# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of
# traits.ui.api as well.
from ..view import View

from ..item import Item

from ..ui_traits import style_trait, AView

from ..editor_factory import EditorFactory

from ..toolkit import toolkit_object

# Currently, this traits is used only for the wx backend.
from ..helper import DockStyle

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Trait whose value is a BaseTraitHandler object
handler_trait = Instance( BaseTraitHandler )

# The visible number of rows displayed
rows_trait = Range( 1, 50, 5,
                    desc = 'the number of list rows to display' )

# The visible number of columns displayed
columns_trait = Range( 1, 10, 1,
                    desc = 'the number of list columns to display' )

editor_trait = Instance( EditorFactory )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for list editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The editor to use for each list item:
    editor = editor_trait

    # Can the list be reorganized, or have items added and deleted.
    mutable = Bool(True)

    # The style of editor to use for each item:
    style = style_trait

    # The trait handler for each list item:
    trait_handler = handler_trait

    # The number of list rows to display:
    rows = rows_trait

    # The number of list columns to create:
    columns = columns_trait

    # Use a notebook for a custom view?
    use_notebook = Bool(False)

    # Show a right-click context menu for the notebook tabs?  (Qt only)
    show_notebook_menu = Bool(False)

    #-- Notebook Specific Traits -----------------------------------------------

    # Are notebook items deletable?
    deletable = Bool(False)

    # FIXME: Currently, this trait is used only in the wx backend.
    # The DockWindow graphical theme
    dock_theme = Any

    # FIXME: Currently, this trait is used only in the wx backend.
    # Dock page style to use for each DockControl:
    dock_style = DockStyle

    # Export class for each item in a notebook:
    export = Str

    # Name of the view to use in notebook mode:
    view = AView

    # The type of UI to construct ('panel', 'subpanel', etc)
    ui_kind = Enum( 'subpanel', 'panel' )

    # A factory function that can be used to define that actual object to be
    # edited (i.e. view_object = factory( object )):
    factory = Callable

    # Extended name to use for each notebook page. It can be either the actual
    # name or the name of an attribute on the object in the form:
    # '.name[.name...]'
    page_name = Str

    # Name of the [object.]trait[.trait...] to synchronize notebook page
    # selection with:
    selected = Str

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    traits_view = View( [ [ 'use_notebook{Use a notebook in a custom view}',
                            '|[Style]' ],
                          [ Item( 'page_name',
                                  enabled_when = 'object.use_notebook' ),
                            Item( 'view',
                                  enabled_when = 'object.use_notebook' ),
                            '|[Notebook options]' ],
                          [ Item( 'rows',
                                  enabled_when = 'not object.use_notebook' ),
                            '|[Number of list rows to display]<>' ] ] )

    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def _get_custom_editor_class ( self ):
        if self.use_notebook:
            return toolkit_object('list_editor:NotebookEditor')
        return toolkit_object('list_editor:CustomEditor')

#-------------------------------------------------------------------------------
#  'ListItemProxy' class:
#   This class is used to update the list editors when the object changes
#   external to the editor.
#-------------------------------------------------------------------------------

class ListItemProxy ( HasTraits ):

    # The list proxy:
    list = Property

    # The item proxies index into the original list:
    index = Int

    # Delegate all other traits to the original object:
    _ = PrototypedFrom( '_zzz_object' )

    # Define all of the private internal use values (the funny names are an
    # attempt to avoid name collisions with delegated trait names):
    _zzz_inited = Any
    _zzz_object = Any
    _zzz_name   = Any

    def __init__ ( self, object, name, index, trait, value ):
        super( ListItemProxy, self ).__init__()

        self._zzz_inited = False
        self._zzz_object = object
        self._zzz_name   = name
        self.index       = index

        if trait is not None:
            self.add_trait( 'value', trait )
            self.value = value

        self._zzz_inited = (self.index < len( self.list ))

    def _get_list ( self ):
        return getattr( self._zzz_object, self._zzz_name )

    def _value_changed ( self, old_value, new_value ):
        if self._zzz_inited:
            self.list[ self.index ] = new_value


# Define the ListEditor class
ListEditor = ToolkitEditorFactory

### EOF ---------------------------------------------------------------------
