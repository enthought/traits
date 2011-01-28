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
#
#------------------------------------------------------------------------------
""" Defines the tree editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Any, Dict, Bool, Tuple, Int, List, Instance, Str, Enum

from ..tree_node import TreeNode

from ..dock_window_theme import DockWindowTheme

from ..editor_factory import EditorFactory

from ..helper import Orientation

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Size of each tree node icon
IconSize = Tuple( ( 16, 16 ), Int, Int )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for tree editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Supported TreeNode objects
    nodes = List( TreeNode )

    # Mapping from TreeNode tuples to MultiTreeNodes
    multi_nodes = Dict

    # Are the individual nodes editable?
    editable = Bool(True)

    # Selection mode.
    selection_mode = Enum('single', 'extended')

    # Is the editor shared across trees?
    shared_editor = Bool(False)

    # Reference to a shared object editor
    editor = Instance( EditorFactory )

    # The DockWindow graphical theme
    # FIXME: Implemented only in wx backend.
    dock_theme = Instance( DockWindowTheme )

    # Show icons for tree nodes?
    show_icons = Bool(True)

    # Hide the tree root node?
    hide_root = Bool(False)

    # Layout orientation of the tree and the editor
    orientation = Orientation

    # Number of tree levels (down from the root) that should be automatically
    # opened
    auto_open = Int

    # Size of the tree node icons
    # FIXME: Document as unimplemented or wx specific.
    icon_size = IconSize

    # Called when a node is selected
    on_select = Any

    # Called when a node is clicked
    on_click = Any

    # Called when a node is double-clicked
    on_dclick = Any

    # Call when the mouse hovers over a node
    on_hover = Any

    # The optional extended trait name of the trait to synchronize with the
    # editor's current selection:
    selected = Str

    # The optional extended trait name of the trait that should be assigned
    # a node object when a tree node is clicked on (Note: If you want to
    # receive repeated clicks on the same node, make sure the trait is defined
    # as an Event):
    click = Str

    # The optional extended trait name of the trait that should be assigned
    # a node object when a tree node is double-clicked on (Note: if you want to
    # receive repeated double-clicks on the same node, make sure the trait is
    # defined as an Event):
    dclick = Str

    # The optional extended trait name of the trait event that is fired
    # whenever the application wishes to veto a tree action in progress (e.g.
    # double-clicking a non-leaf tree node normally opens or closes the node,
    # but if you are handling the double-click event in your program, you may
    # wish to veto the open or close operation). Be sure to fire the veto event
    # in the event handler triggered by the operation (e.g. the 'dclick' event
    # handler.
    veto = Str

    # Mode for lines connecting tree nodes
    #
    # * 'appearance': Show lines only when they look good.
    # * 'on': Always show lines.
    # * 'off': Don't show lines.
    lines_mode = Enum ( 'appearance', 'on', 'off' )
    # FIXME: Document as unimplemented or wx specific.


# Define the TreeEditor class.
TreeEditor = ToolkitEditorFactory

### EOF #######################################################################


