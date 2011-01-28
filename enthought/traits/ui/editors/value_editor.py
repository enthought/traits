#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   01/05/2006
#
#------------------------------------------------------------------------------

""" Defines the tree-based Python value editor and the value editor factory.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Instance, Int, false

from .tree_editor import TreeEditor
from ..view import View
from ..item import Item

from ..value_tree import RootNode, value_tree_nodes

from ..editor_factory import EditorFactory

from ..editor import Editor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class _ValueEditor ( Editor ):
    """ Simple style of editor for values, which displays a tree.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the editor read only?
    readonly = false

    # The root node of the value tree
    root = Instance( RootNode )

    # Is the value editor scrollable? This values overrides the default.
    scrollable = True

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.update_editor()
        editor = TreeEditor(
            auto_open = self.factory.auto_open,
            hide_root = True,
            editable  = False,
            nodes     = value_tree_nodes
        )
        self._ui = self.edit_traits( parent = parent, view =
                       View(
                           Item( 'root',
                                 show_label = False,
                                 editor     = editor
                           ),
                           kind = 'subpanel'
                       )
                   )
        self._ui.parent = self.ui
        self.control    = self._ui.control

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        self.root = RootNode( name     = '',
                              value    = self.value,
                              readonly = self.readonly )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._ui.dispose()

        super( _ValueEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._ui.get_error_controls()

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for tree-based value editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Number of tree levels to automatically open
    auto_open = Int( 2 )

# Define the ValueEditor class.
ValueEditor = ToolkitEditorFactory

#--EOF-------------------------------------------------------------------------
