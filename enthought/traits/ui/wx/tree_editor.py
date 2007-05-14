#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Date: 12/03/2004
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the tree editor and the tree editor factory, for the wxPython user 
interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import generators

import os
import wx
import copy

try:
    from enthought.util.wx.drag_and_drop import PythonDropSource, \
                                                PythonDropTarget
except:
    PythonDropSource = PythonDropTarget = None

from enthought.pyface.resource_manager \
    import resource_manager

from enthought.pyface.image_list \
    import ImageList

from enthought.traits.api \
    import HasTraits, HasStrictTraits, Trait, Any, Dict, true, false, Tuple, \
           Int, List, Instance, Str, Event, Enum

from enthought.traits.trait_base \
    import enumerate

from enthought.traits.ui.api \
    import View, Item, TreeNode, ObjectTreeNode, MultiTreeNode

from enthought.traits.ui.undo \
    import ListUndoItem

from enthought.traits.ui.menu \
    import Menu, Action, Separator

from enthought.pyface.dock.core \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from editor \
    import Editor

from editor_factory \
    import EditorFactory

from helper \
    import Orientation

#-------------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------------

# Paste buffer for copy/cut/paste operations
paste_buffer = None

#-------------------------------------------------------------------------------
#  The core tree node menu actions:
#-------------------------------------------------------------------------------

NewAction    = 'NewAction'
CopyAction   = Action( name         = 'Copy',
                       action       = 'editor._menu_copy_node',
                       enabled_when = 'editor._is_copyable(object)' )
CutAction    = Action( name         = 'Cut',
                       action       = 'editor._menu_cut_node',
                       enabled_when = 'editor._is_cutable(object)' )
PasteAction  = Action( name         = 'Paste',
                       action       = 'editor._menu_paste_node',
                       enabled_when = 'editor._is_pasteable(object)' )
DeleteAction = Action( name         = 'Delete',
                       action       = 'editor._menu_delete_node',
                       enabled_when = 'editor._is_deletable(object)' )
RenameAction = Action( name         = 'Rename',
                       action       = 'editor._menu_rename_node',
                       enabled_when = 'editor._is_renameable(object)' )

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Size of each tree node icon
IconSize = Tuple( ( 16, 16 ), Int, Int )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for tree editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Supported TreeNode objects
    nodes = List( TreeNode )

    # Mapping from TreeNode tuples to MultiTreeNodes
    multi_nodes = Dict

    # Are the individual nodes editable?
    editable = true

    # Is the editor shared across trees?
    shared_editor = false

    # Reference to a shared object editor
    editor = Instance( EditorFactory )

    # Show icons for tree nodes?
    show_icons = true

    # Hide the tree root node?
    hide_root = false

    # Layout orientation of the tree and the editor
    orientation = Orientation

    # Number of tree levels (down from the root) that should be automatically
    # opened
    auto_open = Int

    # Size of the tree node icons
    icon_size = IconSize

    # Called when a node is selected
    on_select = Any

    # Called when a node is double-clicked
    on_dclick = Any

    # The name of the external object trait to synchronize with the editor's
    # **selected** trait:
    selected = Str

    # Mode for lines connecting tree nodes 
    #
    # * 'appearance': Show lines only when they look good.
    # * 'on': Always show lines.
    # * 'off': Don't show lines.
    lines_mode = Enum ( 'appearance', 'on', 'off' )

    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of tree editor.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the tree editor is scrollable? This value overrides the default.
    scrollable = True

    # Allows an external agent to set the tree selection
    selection = Event

    # The currently selected object
    selected = Any

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        style = self._get_style()

        if factory.editable:

            # Check to see if the tree view is based on a shared trait editor:
            if factory.shared_editor:
                factory_editor = factory.editor

                # If this is the editor that defines the trait editor panel:
                if factory_editor is None:

                    # Remember which editor has the trait editor in the factory:
                    factory._editor = self

                    # Create the trait editor panel:
                    self.control = wx.Panel( parent, -1 )
                    self.control._node_ui = self.control._editor_nid = None

                    # Check to see if there are any existing editors that are
                    # waiting to be bound to the trait editor panel:
                    editors = factory._shared_editors
                    if editors is not None:
                        for editor in factory._shared_editors:

                            # If the editor is part of this UI:
                            if editor.ui is self.ui:

                                # Then bind it to the trait editor panel:
                                editor._editor = self.control

                        # Indicate all pending editors have been processed:
                        factory._shared_editors = None

                    # We only needed to build the trait editor panel, so exit:
                    return

                # Check to see if the matching trait editor panel has been
                # created yet:
                editor = factory_editor._editor
                if (editor is None) or (editor.ui is not self.ui):
                    # If not, add ourselves to the list of pending editors:
                    shared_editors = factory_editor._shared_editors
                    if shared_editors is None:
                        factory_editor._shared_editors = shared_editors = []
                    shared_editors.append( self )
                else:
                    # Otherwise, bind our trait editor panel to the shared one:
                    self._editor = editor.control

                # Finally, create only the tree control:
                self.control = self._tree = tree = wx.TreeCtrl( parent, -1,
                                                                style = style )
            else:
                # If editable, create a tree control and an editor panel:
                self._is_dock_window    = True
                self.control = splitter = DockWindow( parent ).control
                self._tree   = tree     = wx.TreeCtrl( splitter, -1,
                                                       style = style )
                self._editor = editor   = wx.ScrolledWindow( splitter )
                editor.SetSizer( wx.BoxSizer( wx.VERTICAL ) )
                editor.SetScrollRate( 16, 16 )
                editor.SetMinSize( wx.Size( 0, 0 ) )

                self._editor._node_ui = self._editor._editor_nid = None
                item = self.item
                hierarchy_name = editor_name = ''
                style = 'fixed'
                name  = item.label
                if name != '':
                    hierarchy_name = name + ' Hierarchy'
                    editor_name    = name + ' Editor'
                    style          = item.dock

                splitter.SetSizer( DockSizer( contents =
                    DockSection( contents = [
                        DockRegion( contents = [
                            DockControl( name    = hierarchy_name,
                                         id      = 'tree',
                                         control = tree,
                                         style   = style ) ] ),
                        DockRegion( contents = [
                            DockControl( name    = editor_name,
                                         id      = 'editor',
                                         control = self._editor,
                                         style   = style ) ] ) ],
                        is_row = (factory.orientation == 'horizontal') ) ) )
        else:
            # Otherwise, just create the tree control:
            self.control = self._tree = tree = wx.TreeCtrl( parent, -1,
                                                            style = style )

        # Set up to show tree node icon (if requested):
        if factory.show_icons:
            self._image_list = ImageList( *factory.icon_size )
            tree.AssignImageList( self._image_list )

        # Set up the mapping between objects and tree id's:
        self._map = {}

        # Initialize the 'undo state' stack:
        self._undoable = []

        # Get the tree control id:
        tid = tree.GetId()

        # Set up the tree event handlers:
        wx.EVT_RIGHT_DOWN(            tree,      self._on_right_down )
        wx.EVT_TREE_ITEM_EXPANDING(   tree, tid, self._on_tree_item_expanding )
        wx.EVT_TREE_ITEM_EXPANDED(    tree, tid, self._on_tree_item_expanded )
        wx.EVT_TREE_ITEM_COLLAPSING(  tree, tid, self._on_tree_item_collapsing )
        wx.EVT_TREE_ITEM_COLLAPSED(   tree, tid, self._on_tree_item_collapsed )
        wx.EVT_TREE_ITEM_ACTIVATED(   tree, tid, self._on_tree_item_activated )
        wx.EVT_TREE_SEL_CHANGED(      tree, tid, self._on_tree_sel_changed )
        wx.EVT_TREE_BEGIN_DRAG(       tree, tid, self._on_tree_begin_drag )
        wx.EVT_TREE_BEGIN_LABEL_EDIT( tree, tid, self._on_tree_begin_label_edit)
        wx.EVT_TREE_END_LABEL_EDIT(   tree, tid, self._on_tree_end_label_edit )

        # Synchronize external object traits with the editor:
        self.sync_value( factory.selected, 'selected' )

        # Set up the drag and drop target:
        if PythonDropTarget is not None:
            tree.SetDropTarget( PythonDropTarget( self ) )

    #---------------------------------------------------------------------------
    #  Handles the 'selection' trait being changed:
    #---------------------------------------------------------------------------

    def _selection_changed ( self, selection ):
        """ Handles the **selection** event.
        """
        try:
            self._tree.SelectItem( self._object_info( selection )[2] )
        except:
            pass

    #---------------------------------------------------------------------------
    #  Handles the 'selected' trait being changed:
    #---------------------------------------------------------------------------

    def _selected_changed ( self, selected ):
        """ Handles the **selected** trait being changed.
        """
        if not self._no_update_selected:
            self._selection_changed( selected )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._tree is not None:
            nid = self._tree.GetRootItem()
            if nid.IsOk():
                self._delete_node( nid )
        super( SimpleEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Returns the style settings used for displaying the wx tree:
    #---------------------------------------------------------------------------

    def _get_style ( self ):
        """ Returns the style settings used for displaying the wx tree.
        """
        factory = self.factory
        style = wx.TR_EDIT_LABELS | wx.TR_HAS_BUTTONS | wx.CLIP_CHILDREN

        # Turn lines off if explicit or for appearance on *nix:
        if ( factory.lines_mode == 'off' ) or \
           ( factory.lines_mode == 'appearance' and os.name == 'posix' ) :
               style |= wx.TR_NO_LINES

        if factory.hide_root:
            style |= (wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT)

        return style

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = self._get_value()
            self.control.SetBackgroundColour( OKColor )
            self.control.Refresh()
        except TraitError, excp:
            pass

    #---------------------------------------------------------------------------
    #  Saves the current 'expanded' state of all tree nodes:
    #---------------------------------------------------------------------------

    def _save_state ( self ):
        tree  = self._tree
        nid   = tree.GetRootItem()
        state = {}
        if nid.IsOk():
            nodes_to_do = [ nid ]
            while nodes_to_do:
                node = nodes_to_do.pop()
                data = self._get_node_data( node )
                try:
                    is_expanded = tree.IsExpanded( node )
                except:
                    is_expanded = True
                state[ hash( data[-1] ) ] = ( data[0], is_expanded )
                for cnid in self._nodes( node ):
                    nodes_to_do.append( cnid )
        return state

    #---------------------------------------------------------------------------
    #  Restores the 'expanded' state of all tree nodes:
    #---------------------------------------------------------------------------

    def _restore_state ( self, state ):
        if not state:
            return
        tree = self._tree
        nid  = tree.GetRootItem()
        if nid.IsOk():
            nodes_to_do = [ nid ]
            while nodes_to_do:
                node = nodes_to_do.pop()
                for cnid in self._nodes( node ):
                    data = self._get_node_data( cnid )
                    key  = hash( data[-1] )
                    if key in state:
                        was_expanded, current_state = state[ key ]
                        if was_expanded:
                            self._expand_node( cnid )
                            if current_state:
                                tree.Expand( cnid )
                            nodes_to_do.append( cnid )

    #---------------------------------------------------------------------------
    #  Expands all nodes starting from the current selection:
    #---------------------------------------------------------------------------

    def expand_all ( self ):
        """ Expands all nodes, starting from the selected node.
        """
        tree = self._tree

        def _do_expand ( nid ):
            expanded, node, object = self._get_node_data( nid )
            if node._has_children( object ):
                tree.SetItemHasChildren( nid, True )
                self._expand_node( nid )
                tree.Expand( nid )

        nid = tree.GetSelection()
        if nid.IsOk():
            nodes_to_do = [ nid ]
            while nodes_to_do:
                node = nodes_to_do.pop()
                _do_expand( node )
                for n in self._nodes( node ):
                    _do_expand( n )
                    nodes_to_do.append( n )

    #---------------------------------------------------------------------------
    #  Expands from the specified node the specified number of sub-levels:
    #---------------------------------------------------------------------------

    def expand_levels ( self, nid, levels, expand = True ):
        """ Expands from the specified node the specified number of sub-levels.
        """
        if levels > 0:
            expanded, node, object = self._get_node_data( nid )
            if node._has_children( object ):
                self._tree.SetItemHasChildren( nid, True )
                self._expand_node( nid )
                if expand:
                    self._tree.Expand( nid )
                for cnid in self._nodes( nid ):
                    self.expand_levels( cnid, levels - 1 )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        tree        = self._tree
        saved_state = {}
        if tree is not None:
            nid = tree.GetRootItem()
            if nid.IsOk():
                #saved_state = self._save_state()
                self._delete_node( nid )
            object, node = self._node_for( self.value )
            if node is not None:
                icon = self._get_icon( node, object )
                self._root_nid = nid = tree.AddRoot( node.get_label( object ),
                                                     icon, icon )
                self._map[ id( object ) ] = [ ( node.children, nid ) ]
                self._add_listeners( node, object )
                self._set_node_data( nid, ( False, node, object) )
                if self.factory.hide_root or node._has_children( object ):
                    tree.SetItemHasChildren( nid, True )
                    self._expand_node( nid )
                    if not self.factory.hide_root:
                        tree.Expand( nid )
                        tree.SelectItem( nid )

                #self._restore_state( saved_state )
                self.expand_levels( nid, self.factory.auto_open, False )
            # fixme: Clear the current editor (if any)...

    #---------------------------------------------------------------------------
    #  Appends a new node to the specified node:
    #---------------------------------------------------------------------------

    def _append_node ( self, nid, node, object ):
        """ Appends a new node to the specified node.
        """
        tree = self._tree
        icon = self._get_icon( node, object )
        cnid = tree.AppendItem( nid, node.get_label( object ), icon, icon )
        has_children = node._has_children( object )
        tree.SetItemHasChildren( cnid, has_children )
        self._set_node_data( cnid, ( False, node, object ) )
        self._map.setdefault( id( object ), [] ).append(
            ( node.children, cnid ) )
        self._add_listeners( node, object )

        # Automatically expand the new node (if requested):
        if has_children and node.can_auto_open( object ):
            tree.Expand( cnid )

        # Return the newly created node:
        return cnid

    #---------------------------------------------------------------------------
    #  Deletes a specified tree node and all its children:
    #---------------------------------------------------------------------------

    def _delete_node ( self, nid ):
        """ Deletes a specified tree node and all its children.
        """
        for cnid in [ cnid for cnid in self._nodes( nid ) ]:
            self._delete_node( cnid )
        expanded, node, object = self._get_node_data( nid )
        self._remove_listeners( node, object )

        # If a node has several named children (i.e. has several traits which
        # define separate sub-nodes for the main node for the object), then
        # there will be several nodes that refer to the same object (i.e. the
        # parent node and each of the trait sub-nodes). Only the parent node
        # can be deleted, but because of the recursive nature of this method,
        # the first deleted sub-node will cause the object to be removed from
        # the map (below). This is why the 'del' is wrapped in a 'try' block...
        # to catch the error when the n'th sub-node or parent sub-node tries
        # to delete the already deleted object from the map.
        try:
            del self._map[ id( object ) ]
        except:
            pass

        # We set the '_locked' flag here because wx seems to generate a
        # 'node selected' event when the node is deleted. This can lead to
        # some bad side effects. So the 'node selected' event handler exits
        # immediately if the '_locked' flag is set:
        self._locked = True
        self._tree.Delete( nid )
        self._locked = False

        # If the deleted node had an active editor panel showing, remove it:
        if (self._editor is not None) and (nid == self._editor._editor_nid):
            self._clear_editor()

    #---------------------------------------------------------------------------
    #  Expands the contents of a specified node (if required):
    #---------------------------------------------------------------------------

    def _expand_node ( self, nid ):
        """ Expands the contents of a specified node (if required).
        """
        expanded, node, object = self._get_node_data( nid )

        # Lazily populate the item's children:
        if not expanded:
            for child in node.get_children( object ):
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )

            # Indicate the item is now populated:
            self._set_node_data( nid, ( True, node, object) )

    #---------------------------------------------------------------------------
    #  Returns each of the child nodes of a specified node id:
    #---------------------------------------------------------------------------

    def _nodes ( self, nid ):
        """ Returns each of the child nodes of a specified node.
        """
        tree         = self._tree
        cnid, cookie = tree.GetFirstChild( nid )
        while cnid.IsOk():
            yield cnid
            cnid, cookie = tree.GetNextChild( nid, cookie )

    #---------------------------------------------------------------------------
    #  Return the index of a specified node id within its parent:
    #---------------------------------------------------------------------------

    def _node_index ( self, nid ):
        pnid = self._tree.GetItemParent( nid )
        if not pnid.IsOk():
            return ( None, None, None )
        for i, cnid in enumerate( self._nodes( pnid ) ):
            if cnid == nid:
                ignore, pnode, pobject = self._get_node_data( pnid )
                return ( pnode, pobject, i )

    #---------------------------------------------------------------------------
    #  Returns the icon index for the specified object:
    #---------------------------------------------------------------------------

    def _get_icon ( self, node, object, is_expanded = False ):
        """ Returns the index of the specified object icon.
        """
        if self._image_list is None:
            return -1

        icon_name = node.get_icon( object, is_expanded )
        if isinstance( icon_name, basestring ):
            if icon_name[:1] == '<':
                icon_name = icon_name[1:-1]
                path      = self
            else:
                path = node.get_icon_path( object )
                if isinstance(path, basestring):
                    path = [ path, node ]
                else:
                    path.append( node )
            reference = resource_manager.locate_image( icon_name, path )
            if reference is None:
                return -1
            file_name = reference.filename
        else:
            # Assume it is an ImageResource, and get its file name directly:
            file_name = icon_name.absolute_path

        return self._image_list.GetIndex( file_name )

    #---------------------------------------------------------------------------
    #  Adds the event listeners for a specified object:
    #---------------------------------------------------------------------------

    def _add_listeners ( self, node, object ):
        """ Adds the event listeners for a specified object.
        """
        if node.allows_children( object ):
            node.when_children_replaced( object, self._children_replaced, False)
            node.when_children_changed(  object, self._children_updated,  False)
        node.when_label_changed( object, self._label_updated, False )

    #---------------------------------------------------------------------------
    #  Removes any event listeners from a specified object:
    #---------------------------------------------------------------------------

    def _remove_listeners ( self, node, object ):
        """ Removes any event listeners from a specified object.
        """
        if node.allows_children( object ):
            node.when_children_replaced( object, self._children_replaced, True )
            node.when_children_changed(  object, self._children_updated,  True )
        node.when_label_changed( object, self._label_updated, True )

    #---------------------------------------------------------------------------
    #  Returns the tree node data for a specified object in the form
    #  ( expanded, node, nid ):
    #---------------------------------------------------------------------------

    def _object_info ( self, object, name = '' ):
        """ Returns the tree node data for a specified object in the form
            ( expanded, node, nid ).
        """
        info = self._map[ id( object ) ]
        for name2, nid in info:
            if name == name2:
                break
        else:
            nid = info[0][1]
        expanded, node, ignore = self._get_node_data( nid )
        return ( expanded, node, nid )

    #---------------------------------------------------------------------------
    #  Returns the TreeNode associated with a specified object:
    #---------------------------------------------------------------------------

    def _node_for ( self, object ):
        """ Returns the TreeNode associated with a specified object.
        """
        if ((type( object ) is tuple) and (len( object ) == 2) and
            isinstance( object[1], TreeNode )):
            return object

        # Select all nodes which understand this object:
        factory = self.factory
        nodes   = [ node for node in factory.nodes
                    if node.is_node_for( object ) ]

        # If only one found, we're done, return it:
        if len( nodes ) == 1:
            return ( object, nodes[0] )

        # If none found, give up:
        if len( nodes ) == 0:
            return ( object, None )

        # Use all selected nodes that have the same 'node_for' list as the
        # first selected node:
        base  = nodes[0].node_for
        nodes = [ node for node in nodes if base == node.node_for ]

        # If only one left, then return that node:
        if len( nodes ) == 1:
            return ( object, nodes[0] )

        # Otherwise, return a MultiTreeNode based on all selected nodes...

        # Use the node with no specified children as the root node. If not
        # found, just use the first selected node as the 'root node':
        root_node = None
        for i, node in enumerate( nodes ):
            if node.children == '':
                root_node = node
                del nodes[i]
                break
        else:
            root_node = nodes[0]

        # If we have a matching MultiTreeNode already cached, return it:
        key = ( root_node, ) + tuple( nodes )
        if key in factory.multi_nodes:
            return ( object, factory.multi_nodes[ key ] )

        # Otherwise create one, cache it, and return it:
        factory.multi_nodes[ key ] = multi_node = MultiTreeNode(
                                                       root_node = root_node,
                                                       nodes     = nodes )

        return ( object, multi_node )

    #---------------------------------------------------------------------------
    #  Returns the TreeNode associated with a specified class:
    #---------------------------------------------------------------------------

    def _node_for_class ( self, klass ):
        """ Returns the TreeNode associated with a specified class.
        """
        for node in self.factory.nodes:
            if issubclass( klass, tuple( node.node_for ) ):
                return node
        return None

    #---------------------------------------------------------------------------
    #  Returns the node and class associated with a specified class name:
    #---------------------------------------------------------------------------

    def _node_for_class_name ( self, class_name ):
        """ Returns the node and class associated with a specified class name.
        """
        for node in self.factory.nodes:
            for klass in node.node_for:
                if class_name == klass.__name__:
                    return ( node, klass )
        return ( None, None )

    #---------------------------------------------------------------------------
    #  Updates the icon for a specified node:
    #---------------------------------------------------------------------------

    def _update_icon ( self, event, is_expanded ):
        """ Updates the icon for a specified node.
        """
        self._update_icon_for_nid( event.GetItem() )

    #---------------------------------------------------------------------------
    #  Updates the icon for a specified node id:
    #---------------------------------------------------------------------------

    def _update_icon_for_nid ( self, nid ):
        """ Updates the icon for a specified node ID.
        """
        if self._image_list is not None:
            expanded, node, object = self._get_node_data( nid )
            icon = self._get_icon( node, object, expanded )
            self._tree.SetItemImage( nid, icon, wx.TreeItemIcon_Normal )
            self._tree.SetItemImage( nid, icon, wx.TreeItemIcon_Selected )

    #---------------------------------------------------------------------------
    #  Unpacks an event to see whether a tree item was involved:
    #---------------------------------------------------------------------------

    def _unpack_event ( self, event ):
        """ Unpacks an event to see whether a tree item was involved.
        """
        try:
            point = event.GetPosition()
        except:
            point = event.GetPoint()

        nid = None
        if hasattr( event, 'GetItem' ):
            nid = event.GetItem()
        if (nid is None) or (not nid.IsOk()):
            nid, flags = self._tree.HitTest( point )
        if nid.IsOk():
            return self._get_node_data( nid ) + ( nid, point )
        return ( None, None, None, nid, point )

    #---------------------------------------------------------------------------
    #  Returns information about the node at a specified point:
    #---------------------------------------------------------------------------

    def _hit_test ( self, point ):
        """ Returns information about the node at a specified point.
        """
        nid, flags = self._tree.HitTest( point )
        if nid.IsOk():
            return self._get_node_data( nid ) + ( nid, point )
        return ( None, None, None, nid, point )

    #---------------------------------------------------------------------------
    #  Begins an 'undoable' transaction:
    #---------------------------------------------------------------------------

    def _begin_undo ( self ):
        """ Begins an "undoable" transaction.
        """
        ui = self.ui
        self._undoable.append( ui._undoable )
        if (ui._undoable == -1) and (ui.history is not None):
            ui._undoable = ui.history.now

    #---------------------------------------------------------------------------
    #  Ends an 'undoable' transaction:
    #---------------------------------------------------------------------------

    def _end_undo ( self ):
        if self._undoable.pop() == -1:
            self.ui._undoable = -1

    #---------------------------------------------------------------------------
    #  Gets an 'undo' item for a change made to a node's children:
    #---------------------------------------------------------------------------

    def _get_undo_item ( self, object, name, event ):
        return ListUndoItem( object  = object,
                             name    = name,
                             index   = event.index,
                             added   = event.added,
                             removed = event.removed )

    #---------------------------------------------------------------------------
    #  Performs an undoable 'append' operation:
    #---------------------------------------------------------------------------

    def _undoable_append ( self, node, object, data, make_copy = True ):
        """ Performs an undoable append operation.
        """
        try:
            self._begin_undo()
            if make_copy:
                data = copy.deepcopy( data )
            node.append_child( object, data )
        finally:
            self._end_undo()

    #---------------------------------------------------------------------------
    #  Performs an undoable 'insert' operation:
    #---------------------------------------------------------------------------

    def _undoable_insert ( self, node, object, index, data, make_copy = True ):
        """ Performs an undoable insert operation.
        """
        try:
            self._begin_undo()
            if make_copy:
                data = copy.deepcopy( data )
            node.insert_child( object, index, data )
        finally:
            self._end_undo()

    #---------------------------------------------------------------------------
    #  Performs an undoable 'delete' operation:
    #---------------------------------------------------------------------------

    def _undoable_delete ( self, node, object, index ):
        """ Performs an undoable delete operation.
        """
        try:
            self._begin_undo()
            node.delete_child( object, index )
        finally:
            self._end_undo()

    #---------------------------------------------------------------------------
    #  Gets the id associated with a specified object (if any):
    #---------------------------------------------------------------------------

    def _get_object_nid ( self, object, name = '' ):
        """ Gets the ID associated with a specified object (if any).
        """
        info = self._map.get( id( object ) )
        if info is None:
            return None
        for name2, nid in info:
            if name == name2:
                return nid
        else:
            return info[0][1]

    #---------------------------------------------------------------------------
    #  Clears the current editor pane (if any):
    #---------------------------------------------------------------------------

    def _clear_editor ( self ):
        """ Clears the current editor pane (if any).
        """
        editor = self._editor
        if editor._node_ui is not None:
            editor.SetSizer( None )
            editor._node_ui.dispose()
            editor._node_ui = editor._editor_nid = None

    #---------------------------------------------------------------------------
    #  Gets/Sets the node specific data:
    #---------------------------------------------------------------------------

    def _get_node_data ( self, nid ):
        """ Gets the node specific data.
        """
        if nid == self._root_nid:
            return self._root_nid_data
        return self._tree.GetPyData( nid )

    def _set_node_data ( self, nid, data ):
        """ Sets the node specific data.
        """
        if nid == self._root_nid:
            self._root_nid_data = data
        else:
            self._tree.SetPyData( nid, data )

#----- User callable methods: --------------------------------------------------

    #---------------------------------------------------------------------------
    #  Gets the object associated with a specified node:
    #---------------------------------------------------------------------------

    def get_object ( self, nid ):
        """ Gets the object associated with a specified node.
        """
        return self._get_node_data( nid )[2]

    #---------------------------------------------------------------------------
    #  Returns the object which is the immmediate parent of a specified object
    #  in the tree:
    #---------------------------------------------------------------------------

    def get_parent ( self, object, name = '' ):
        """ Returns the object that is the immmediate parent of a specified
            object in the tree.
        """
        nid = self._get_object_nid( object, name )
        if nid is not None:
            pnid = self._tree.GetItemParent( nid )
            if pnid.IsOk():
                return self.get_object( pnid )
        return None

    #---------------------------------------------------------------------------
    #  Returns the node associated with a specified object:
    #---------------------------------------------------------------------------

    def get_node ( self, object, name = '' ):
        """ Returns the node associated with a specified object.
        """
        nid = self._get_object_nid( object, name )
        if nid is not None:
            return self._get_node_data( nid )[1]
        return None

#----- Tree event handlers: ----------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles a tree node expanding:
    #---------------------------------------------------------------------------

    def _on_tree_item_expanding ( self, event ):
        """ Handles a tree node expanding.
        """
        if self._veto:
            self._veto = False
            event.Veto()
            return

        nid  = event.GetItem()
        tree = self._tree
        expanded, node, object = self._get_node_data( nid )

        # If 'auto_close' requested for this node type, close all of the node's
        # siblings:
        if node.can_auto_close( object ):
            snid = nid
            while True:
                snid = tree.GetPrevSibling( snid )
                if not snid.IsOk():
                    break
                tree.Collapse( snid )
            snid = nid
            while True:
                snid = tree.GetNextSibling( snid )
                if not snid.IsOk():
                    break
                tree.Collapse( snid )

        # Expand the node (i.e. populate its children if they are not there
        # yet):
        self._expand_node( nid )

    #---------------------------------------------------------------------------
    #  Handles a tree node being expanded:
    #---------------------------------------------------------------------------

    def _on_tree_item_expanded ( self, event ):
        """ Handles a tree node being expanded.
        """
        self._update_icon( event, True )

    #---------------------------------------------------------------------------
    #  Handles a tree node collapsing:
    #---------------------------------------------------------------------------

    def _on_tree_item_collapsing ( self, event ):
        """ Handles a tree node collapsing.
        """
        if self._veto:
            self._veto = False
            event.Veto()

    #---------------------------------------------------------------------------
    #  Handles a tree node being collapsed:
    #---------------------------------------------------------------------------

    def _on_tree_item_collapsed ( self, event ):
        """ Handles a tree node being collapsed.
        """
        self._update_icon( event, False )

    #---------------------------------------------------------------------------
    #  Handles a tree node being selected:
    #---------------------------------------------------------------------------

    def _on_tree_sel_changed ( self, event ):
        """ Handles a tree node being selected.
        """
        if self._locked:
            return

        # Get the new selection:
        object      = None
        not_handled = True
        nid         = self._tree.GetSelection()
        if nid.IsOk():
            # If there is a real selection, get the associated object:
            expanded, node, object = self._get_node_data( event.GetItem() )

            # Try to inform the node specific handler of the selection:
            not_handled = node.select( object )

        # Set the value of the new selection:
        self._no_update_selected = True
        self.selected            = object
        self._no_update_selected = False

        # If no one has been notified of the selection yet, inform the editor's
        # select handler (if any) of the new selection:
        if not_handled is True:
            self.ui.evaluate( self.factory.on_select, object )

        # Check to see if there is an associated node editor pane:
        editor = self._editor
        if editor is not None:
            # If we already had a node editor, destroy it:
            editor.Freeze()
            self._clear_editor()

            # If there is a selected object, create a new editor for it:
            if object is not None:
                # Try to chain the undo history to the main undo history:
                view = node.get_view( object )
                if view is None:
                    view = object.trait_view()
                history = self.ui.history
                if (history is not None) or (view.kind == 'subpanel'):
                    ui = object.edit_traits( parent = editor,
                                             view   = view,
                                             kind   = 'subpanel' )
                    ui.history = history
                else:
                    # Otherwise, just set up our own new one:
                    ui = object.edit_traits( parent = editor,
                                             view   = view,
                                             kind   = 'panel' )

                # Remember the new editor's UI and node info:
                editor._node_ui    = ui
                editor._editor_nid = nid

                # Finish setting up the editor:
                sizer = wx.BoxSizer( wx.VERTICAL )
                sizer.Add( ui.control, 1, wx.EXPAND )
                editor.SetSizer( sizer )
                editor.Layout()

            # fixme: The following is a hack needed to make the editor window
            # (which is a wx.ScrolledWindow) recognize that its contents have
            # been changed:
            dx, dy = editor.GetSize()
            editor.SetSize( wx.Size( dx, dy + 1 ) )
            editor.SetSize( wx.Size( dx, dy ) )

            # Allow the editor view to show any changes that have occurred:
            editor.Thaw()

    #---------------------------------------------------------------------------
    #  Handles a tree item being activated (i.e. double clicked):
    #---------------------------------------------------------------------------

    def _on_tree_item_activated ( self, event ):
        """ Handles a tree item being activated (i.e., double-clicked).
        """
        expanded, node, object = self._get_node_data( event.GetItem() )
        if node.dclick( object ) is True:
            if self.factory.on_dclick is not None:
                self.ui.evaluate( self.factory.on_dclick, object )
                self._veto = True
        else:
            self._veto = True

    #---------------------------------------------------------------------------
    #  Handles the user starting to edit a tree node label:
    #---------------------------------------------------------------------------

    def _on_tree_begin_label_edit ( self, event ):
        """ Handles the user starting to edit a tree node label.
        """
        item   = event.GetItem()
        parent = self._tree.GetItemParent( item )
        if parent.IsOk():
            expanded, node, object = self._get_node_data( parent )
            if node.can_rename( object ):
                expanded, node, object = self._get_node_data( item )
                if node.can_rename_me( object ):
                    return
        event.Veto()

    #---------------------------------------------------------------------------
    #  Handles the user completing tree node label editing:
    #---------------------------------------------------------------------------

    def _on_tree_end_label_edit ( self, event ):
        """ Handles the user completing tree node label editing.
        """
        label = event.GetLabel()
        if len( label ) > 0:
            expanded, node, object = self._get_node_data( event.GetItem() )
            # Tell the node to change the label. If it raises an exception,
            # that means it didn't like the label, so veto the tree node change:
            try:
                node.set_label( object, label )
                return
            except:
                pass
        event.Veto()

    #---------------------------------------------------------------------------
    #  Handles a drag operation starting on a tree node:
    #---------------------------------------------------------------------------

    def _on_tree_begin_drag ( self, event ):
        """ Handles a drag operation starting on a tree node.
        """
        if PythonDropSource is not None:
            expanded, node, object, nid, point = self._unpack_event( event )
            if node is not None:
                try:
                    self._dragging = True
                    PythonDropSource( self._tree,
                                      node.get_drag_object( object ) )
                finally:
                    self._dragging = False

    #---------------------------------------------------------------------------
    #  Handles the user right clicking on a tree node:
    #---------------------------------------------------------------------------

    def _on_right_down ( self, event ):
        """ Handles the user right clicking on a tree node.
        """
        expanded, node, object, nid, point = self._unpack_event( event )

        if node is not None:
            self._data    = ( node, object, nid )
            self._context = { 'object':  object,
                              'editor':  self,
                              'node':    node,
                              'info':    self.ui.info,
                              'handler': self.ui.handler }

            # Try to get the parent node of the node clicked on:
            pnid = self._tree.GetItemParent( nid )
            if pnid.IsOk():
                ignore, parent_node, parent_object = self._get_node_data( pnid )
            else:
                parent_node = parent_object = None

            self._menu_node          = node
            self._menu_parent_node   = parent_node
            self._menu_parent_object = parent_object

            menu = node.get_menu( object )
            if menu is None:
                menu = self._standard_menu( node, object )
            else:
                group = menu.find_group( NewAction )
                if group is not None:
                    # Only set it the first time:
                    group.id = ''
                    actions  = self._new_actions( node, object )
                    if len( actions ) > 0:
                        group.insert( 0, Menu( name = 'New', *actions ) )

            wxmenu = menu.create_menu( self._tree, self )
            self._tree.PopupMenuXY( wxmenu,
                                    point[0] - 10, point[1] - 10 )
            wxmenu.Destroy()
            self._data = self._context = self._menu_node = \
            self._menu_parent_node = self._menu_parent_object = None

    #---------------------------------------------------------------------------
    #  Returns the standard contextual pop-up menu:
    #---------------------------------------------------------------------------

    def _standard_menu ( self, node, object ):
        """ Returns the standard contextual pop-up menu.
        """
        actions = [ CutAction, CopyAction, PasteAction, Separator(),
                    DeleteAction, Separator(), RenameAction ]

        # See if the 'New' menu section should be added:
        items = self._new_actions( node, object )
        if len( items ) > 0:
            actions[0:0] = [ Menu( name = 'New', *items ), Separator() ]

        return Menu( *actions )

    #---------------------------------------------------------------------------
    #  Returns a list of Actions that will create 'new' objects:
    #---------------------------------------------------------------------------

    def _new_actions ( self, node, object ):
        """ Returns a list of Actions that will create new objects.
        """
        object = self._data[1]
        items  = []
        add    = node.get_add( object )
        if len( add ) > 0:
            for klass in add:
                prompt = False
                if isinstance( klass, tuple ):
                    klass, prompt = klass
                add_node = self._node_for_class( klass )
                if add_node is not None:
                    class_name = klass.__name__
                    name       = add_node.get_name( object )
                    if name == '':
                        name = class_name
                    items.append(
                        Action( name   = name,
                                action = "editor._menu_new_node('%s',%s)" %
                                         ( class_name, prompt ) ) )
        return items

    #---------------------------------------------------------------------------
    #  Menu action helper methods:
    #---------------------------------------------------------------------------

    def _is_copyable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            return parent.can_copy( self._menu_parent_object )
        return ((parent is not None) and parent.can_copy( object ))

    def _is_cutable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            can_cut = (parent.can_copy( self._menu_parent_object ) and
                       parent.can_delete( self._menu_parent_object ))
        else:
            can_cut = ((parent is not None) and
                       parent.can_copy( object ) and
                       parent.can_delete( object ))
        return (can_cut and self._menu_node.can_delete_me( object ))

    def _is_pasteable ( self, object ):
        from enthought.util.wx.clipboard import clipboard

        return self._menu_node.can_add( object, clipboard.object_type )

    def _is_deletable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            can_delete = parent.can_delete( self._menu_parent_object )
        else:
            can_delete = ((parent is not None) and parent.can_delete( object ))
        return (can_delete and self._menu_node.can_delete_me( object ))

    def _is_renameable ( self, object ):
        parent = self._menu_parent_node
        if isinstance( parent, ObjectTreeNode ):
            can_rename = parent.can_rename( self._menu_parent_object )
        else:
            can_rename = ((parent is not None) and parent.can_rename( object ))
        return (can_rename and self._menu_node.can_rename_me( object ))

#----- Drag and drop event handlers: -------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles a Python object being dropped on the tree:
    #---------------------------------------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the tree.
        """
        if isinstance( data, list ):
            rc = wx.DragNone
            for item in data:
                rc = self.wx_dropped_on( x, y, item, drag_result )
            return rc

        expanded, node, object, nid, point = self._hit_test( wx.Point( x, y ) )
        if node is not None:
            if drag_result == wx.DragMove:
                if not node._is_droppable( object, data, False ):
                    return wx.DragNone

                if self._dragging:
                    nid  = self._object_info( data )[2]
                    data = node._drop_object( object, data, False )
                    if data is not None:
                        try:
                            self._begin_undo()
                            self._undoable_delete( *self._node_index( nid ) )
                            self._undoable_append( node, object, data, False )
                        finally:
                            self._end_undo()
                else:
                    data = node._drop_object( object, data )
                    if data is not None:
                        self._undoable_append( node, object, data )

                return drag_result

            to_node, to_object, to_index = self._node_index( nid )
            if to_node is not None:
                if self._dragging:
                    nid  = self._object_info( data )[2]
                    data = node._drop_object( to_object, data, False )
                    if data is not None:
                        from_node, from_object, from_index = \
                            self._node_index( nid )
                        if ((to_object is from_object) and
                            (to_index > from_index)):
                            to_index -= 1
                        try:
                            self._begin_undo()
                            self._undoable_delete( from_node, from_object,
                                                   from_index )
                            self._undoable_insert( to_node, to_object, to_index,
                                                   data, False )
                        finally:
                            self._end_undo()
                else:
                    data = to_node._drop_object( to_object, data )
                    if data is not None:
                        self._undoable_insert( to_node, to_object, to_index,
                                               data )

                return drag_result

        return wx.DragNone

    #---------------------------------------------------------------------------
    #  Handles a Python object being dragged over the tree:
    #---------------------------------------------------------------------------

    def wx_drag_over ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        expanded, node, object, nid, point = self._hit_test( wx.Point( x, y ) )
        insert = False
        if (node is not None) and (drag_result == wx.DragCopy):
            node, object, index = self._node_index( nid )
            insert = True
        if (self._dragging and
            (not self._is_drag_ok( self._get_object_nid( data ),
                                   data, object ))):
            return wx.DragNone
        if (node is not None) and node._is_droppable( object, data, insert ):
            return drag_result
        return wx.DragNone

    #---------------------------------------------------------------------------
    #  Makes sure that the target is not the same as or a child of the source
    #  object:
    #---------------------------------------------------------------------------

    def _is_drag_ok ( self, snid, source, target ):
        if (snid is None) or (target is source):
            return False
        for cnid in self._nodes( snid ):
            if not self._is_drag_ok( cnid, self._get_node_data( cnid )[2],
                                     target ):
                return False
        return True


#----- pyface.action 'controller' interface implementation: --------------------

    #---------------------------------------------------------------------------
    #  Adds a menu item to the menu being constructed:
    #---------------------------------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        action = menu_item.item.action
        self.eval_when( action.enabled_when, menu_item, 'enabled' )
        self.eval_when( action.checked_when, menu_item, 'checked' )

    #---------------------------------------------------------------------------
    #  Adds a tool bar item to the tool bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )

    #---------------------------------------------------------------------------
    #  Returns whether the menu action should be defined in the user interface:
    #---------------------------------------------------------------------------

    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        if action.defined_when != '':
            try:
                if not eval( action.defined_when, globals(), self._context ):
                    return False
            except:
                from enthought.debug.fbi import if_fbi
                if_fbi()

        if action.visible_when != '':
            try:
                if not eval( action.visible_when, globals(), self._context ):
                    return False
            except:
                from enthought.debug.fbi import if_fbi
                if_fbi()

        return True

    #---------------------------------------------------------------------------
    #  Returns whether the toolbar action should be defined in the user
    #  interface:
    #---------------------------------------------------------------------------

    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return self.can_add_to_menu( action )

    #---------------------------------------------------------------------------
    #  Performs the action described by a specified Action object:
    #---------------------------------------------------------------------------

    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        self.ui.do_undoable( self._perform, action )

    def _perform ( self, action ):
        node, object, nid = self._data
        method_name       = action.action
        info              = self.ui.info
        handler           = self.ui.handler

        if method_name.find( '.' ) >= 0:
            if method_name.find( '(' ) < 0:
                method_name += '()'
            try:
                eval( method_name, globals(),
                      { 'object':  object,
                        'editor':  self,
                        'node':    node,
                        'info':    info,
                        'handler': handler } )
            except:
                # fixme: Should the exception be logged somewhere?
                pass
            return

        method = getattr( handler, method_name, None )
        if method is not None:
            method( info, object )
            return

        if action.on_perform is not None:
            action.on_perform( object )

#----- Menu support methods: ---------------------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates a condition within a defined context and sets a specified
    #  object trait based on the (assumed) boolean result:
    #---------------------------------------------------------------------------

    def eval_when ( self, condition, object, trait ):
        """ Evaluates a condition within a defined context, and sets a 
        specified object trait based on the result, which is assumed to be a
        Boolean.
        """
        if condition != '':
            value = True
            try:
                if not eval( condition, globals(), self._context ):
                    value = False
            except:
                from enthought.debug.fbi import if_fbi
                if_fbi()
            setattr( object, trait, value )

#----- Menu event handlers: ----------------------------------------------------

    #---------------------------------------------------------------------------
    #  Copies the current tree node object to the paste buffer:
    #---------------------------------------------------------------------------

    def _menu_copy_node ( self ):
        """ Copies the current tree node object to the paste buffer.
        """
        from enthought.util.wx.clipboard import clipboard

        clipboard.data = self._data[1]
        self._data     = None

    #---------------------------------------------------------------------------
    #   Cuts the current tree node object into the paste buffer:
    #---------------------------------------------------------------------------

    def _menu_cut_node ( self ):
        """  Cuts the current tree node object into the paste buffer.
        """
        from enthought.util.wx.clipboard import clipboard

        node, object, nid = self._data
        clipboard.data    = object
        self._data        = None
        self._undoable_delete( *self._node_index( nid ) )

    #---------------------------------------------------------------------------
    #  Pastes the current contents of the paste buffer into the current node:
    #---------------------------------------------------------------------------

    def _menu_paste_node ( self ):
        """ Pastes the current contents of the paste buffer into the current
            node.
        """
        from enthought.util.wx.clipboard import clipboard

        node, object, nid = self._data
        self._data        = None
        self._undoable_append( node, object, clipboard.object_data, False )

    #---------------------------------------------------------------------------
    #  Deletes the current node from the tree:
    #---------------------------------------------------------------------------

    def _menu_delete_node ( self ):
        """ Deletes the current node from the tree.
        """
        node, object, nid = self._data
        self._data        = None
        rc = node.confirm_delete( object )
        if rc is not False:
            if rc is not True:
                if self.ui.history is None:
                    # If no undo history, ask user to confirm the delete:
                    dlg = wx.MessageDialog(
                                self._tree,
                                'Are you sure you want to delete %s?' % node.get_label( object ),
                                'Confirm Deletion',
                                style = wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION )
                    if dlg.ShowModal() != wx.ID_OK:
                        return

            self._undoable_delete( *self._node_index( nid ) )

    #---------------------------------------------------------------------------
    #  Renames the current tree node:
    #---------------------------------------------------------------------------

    def _menu_rename_node ( self ):
        """ Renames the current tree node.
        """
        node, object, nid = self._data
        self._data        = None
        object_label      = ObjectLabel( label = node.get_label( object ) )
        if object_label.edit_traits().result:
            label = object_label.label.strip()
            if label != '':
                node.set_label( object, label )

    #---------------------------------------------------------------------------
    #  Adds a new object to the current node:
    #---------------------------------------------------------------------------

    def _menu_new_node ( self, class_name, prompt = False ):
        """ Adds a new object to the current node.
        """
        node, object, nid   = self._data
        self._data          = None
        new_node, new_class = self._node_for_class_name( class_name )
        new_object          = new_class()
        if (not prompt) or new_object.edit_traits(
                            parent = self.control, kind = 'livemodal' ).result:
            self._undoable_append( node, object, new_object, False )

            # Automatically select the new object if editing is being performed:
            if self.factory.editable:
                self._tree.SelectItem( self._tree.GetLastChild( nid ) )

#----- Model event handlers: ---------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the children of a node being completely replaced:
    #---------------------------------------------------------------------------

    def _children_replaced ( self, object, name = '', new = None ):
        """ Handles the children of a node being completely replaced.
        """
        tree                = self._tree
        expanded, node, nid = self._object_info( object, name )
        children            = node.get_children( object )

        # Only add/remove the changes if the node has already been expanded:
        if expanded:
            # Delete all current child nodes:
            for cnid in [ cnid for cnid in self._nodes( nid ) ]:
                self._delete_node( cnid )

            # Add all of the children back in as new nodes:
            for child in children:
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )

        # Indicate whether the node has any children now:
        tree.SetItemHasChildren( nid, len( children ) > 0 )

        # Try to expand the node (if requested):
        if node.can_auto_open( object ):
            tree.Expand( nid )

    #---------------------------------------------------------------------------
    #  Handles the children of a node being changed:
    #---------------------------------------------------------------------------

    def _children_updated ( self, object, name, event ):
        """ Handles the children of a node being changed.
        """
        # Log the change that was made made (removing '_items' from the end of
        # the name):
        name = name[:-6]
        self.log_change( self._get_undo_item, object, name, event )

        # Get information about the node that was changed:
        tree                = self._tree
        expanded, node, nid = self._object_info( object, name )
        children            = node.get_children( object )

        # If the new children aren't all at the end, just remove/add them all:
        n = len( event.added )
        if (n > 0) and ((event.index + n) != len( children )):
            self._children_replaced( object, name, event )
            return

        # Only add/remove the changes if the node has already been expanded:
        if expanded:
            # Remove all of the children that were deleted:
            for child in event.removed:
                expanded, child_node, cnid = self._object_info( child )
                self._delete_node( cnid )

            # Add all of the children that were added:
            for child in event.added:
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )

        # Indicate whether the node has any children now:
        tree.SetItemHasChildren( nid, len( children ) > 0 )

        # Try to expand the node (if requested):
        root = tree.GetRootItem()
        if node.can_auto_open( object ):
            if ( nid != root ) or not self.factory.hide_root:
                tree.Expand( nid )

    #---------------------------------------------------------------------------
    #   Handles the label of an object being changed:
    #---------------------------------------------------------------------------

    def _label_updated ( self, object, name, label ):
        """  Handles the label of an object being changed.
        """
        nids = {}
        for name2, nid in self._map[ id( object ) ]:
            if nid not in nids:
                nids[ nid ] = None
                node = self._get_node_data( nid )[1]
                self._tree.SetItemText( nid, node.get_label( object ) )
                self._update_icon_for_nid ( nid )

#-- UI preference save/restore interface ---------------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if self._is_dock_window:
            if isinstance( prefs, dict ):
                structure = prefs.get( 'structure' )
            else:
                structure = prefs
            self.control.GetSizer().SetStructure( self.control, structure )

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        if self._is_dock_window:
            return { 'structure': self.control.GetSizer().GetStructure() }

        return None

#-- End UI preference save/restore interface -----------------------------------

#-------------------------------------------------------------------------------
#  'ObjectLabel' class:
#-------------------------------------------------------------------------------

class ObjectLabel ( HasStrictTraits ):
    """ An editable label for an object.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Label to be edited
    label = Str  

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    traits_view = View( 'label',
                        title   = 'Edit Label',
                        kind    = 'modal',
                        buttons = [ 'OK', 'Cancel' ] )

