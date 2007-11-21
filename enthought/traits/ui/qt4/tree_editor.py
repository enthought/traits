#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the tree editor and the tree editor factory, for the PyQt user 
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import copy

from PyQt4 import QtCore, QtGui

from enthought.pyface.resource_manager \
    import resource_manager

from enthought.traits.api \
    import HasTraits, Any, Dict, true, false, Int, List, Instance, Str, Event

from enthought.traits.trait_base \
    import enumerate

from enthought.traits.ui.api \
    import TreeNode, ObjectTreeNode, MultiTreeNode
    
from enthought.traits.ui.undo \
    import ListUndoItem

from enthought.traits.ui.menu \
    import Menu, Action, Separator

from clipboard \
    import clipboard, PyMimeData

from editor \
    import Editor

from editor_factory \
    import EditorFactory

from helper \
    import pixmap_cache, Orientation

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
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for tree editors.
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
    
    # The DockWindow graphical theme
    # FIXME: Document as unimplemented or wx specific.
    #dock_theme = Instance( DockWindowTheme )

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
    # FIXME: Document as unimplemented or wx specific.
    #icon_size = IconSize

    # Called when a node is selected
    on_select = Any

    # Called when a node is clicked
    on_click = Any

    # Called when a node is double-clicked
    on_dclick = Any

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
    # FIXME: Document as unimplemented or wx specific.
    #lines_mode = Enum ( 'appearance', 'on', 'off' )

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

    # The event fired when a tree node is clicked on:
    click = Event

    # The event fired when a tree node is double-clicked on:
    dclick = Event

    # The event fired when the application wants to veto an operation:
    veto = Event

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        self._editor = None

        if factory.editable:

            # Check to see if the tree view is based on a shared trait editor:
            if factory.shared_editor:
                factory_editor = factory.editor

                # If this is the editor that defines the trait editor panel:
                if factory_editor is None:

                    # Remember which editor has the trait editor in the factory:
                    factory._editor = self

                    # Create the trait editor panel:
                    self.control = QtGui.QWidget(panel)
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
                self.control = self._tree = _TreeWidget(self)
            else:
                # If editable, create a tree control and an editor panel:
                self._tree = _TreeWidget(self)

                self._editor = sa = QtGui.QScrollArea()
                sa.setFrameShape(QtGui.QFrame.NoFrame)
                sa._node_ui = sa._editor_nid = None

                if factory.orientation == 'horizontal':
                    orient = QtCore.Qt.Horizontal
                else:
                    orient = QtCore.Qt.Vertical

                self.control = splitter = QtGui.QSplitter(orient)
                splitter.addWidget(self._tree)
                splitter.addWidget(sa)
        else:
            # Otherwise, just create the tree control:
            self.control = self._tree = _TreeWidget(self)

        # Set up the mapping between objects and tree id's:
        self._map = {}

        # Initialize the 'undo state' stack:
        self._undoable = []

        # Synchronize external object traits with the editor:
        self.sync_value( factory.selected, 'selected' )
        self.sync_value( factory.click,    'click',  'to' )
        self.sync_value( factory.dclick,   'dclick', 'to' )
        self.sync_value( factory.veto,     'veto',   'from' )

    #---------------------------------------------------------------------------
    #  Handles the 'selection' trait being changed:
    #---------------------------------------------------------------------------

    def _selection_changed ( self, selection ):
        """ Handles the **selection** event.
        """
        try:
            self._tree.setCurrentItem(self._object_info(selection)[2])
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
    #  Handles the 'veto' event being fired:
    #---------------------------------------------------------------------------

    def _veto_changed ( self ):
        """ Handles the 'veto' event being fired.
        """
        self._veto = True

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self._tree is not None:
            self._delete_node(self._tree.invisibleRootItem())

        super( SimpleEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Expands from the specified node the specified number of sub-levels:
    #---------------------------------------------------------------------------

    def expand_levels ( self, nid, levels, expand = True ):
        """ Expands from the specified node the specified number of sub-levels.
        """
        if levels > 0:
            expanded, node, object = self._get_node_data( nid )
            if node._has_children( object ):
                self._expand_node( nid )
                if expand:
                    nid.setExpanded(True)
                for cnid in self._nodes_for( nid ):
                    self.expand_levels( cnid, levels - 1 )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        tree = self._tree
        saved_state = {}

        tree.clear()

        object, node = self._node_for( self.value )
        if node is not None:
            if self.factory.hide_root:
                nid = tree.invisibleRootItem()
            else:
                nid = QtGui.QTreeWidgetItem(tree)
                nid.setText(0, node.get_label(object))
                nid.setIcon(0, self._get_icon(node, object))

            self._map[ id( object ) ] = [ ( node.children, nid ) ]
            self._add_listeners( node, object )
            self._set_node_data( nid, ( False, node, object) )
            if self.factory.hide_root or node._has_children( object ):
                self._expand_node( nid )
                if not self.factory.hide_root:
                    nid.setExpanded(True)
                    tree.setCurrentItem(nid)

            self.expand_levels( nid, self.factory.auto_open, False )
        # FIXME: Clear the current editor (if any)...

    #---------------------------------------------------------------------------
    #  Appends a new node to the specified node:
    #---------------------------------------------------------------------------

    def _append_node ( self, nid, node, object ):
        """ Appends a new node to the specified node.
        """
        cnid = QtGui.QTreeWidgetItem(nid)
        cnid.setText(0, node.get_label(object))
        cnid.setIcon(0, self._get_icon(node, object))

        has_children = node._has_children(object)
        self._set_node_data( cnid, ( False, node, object ) )
        self._map.setdefault( id( object ), [] ).append(
            ( node.children, cnid ) )
        self._add_listeners( node, object )

        # Automatically expand the new node (if requested):
        if has_children:
            # Qt only draws the control that expands the tree if there is a
            # child.  As the tree is being populated lazily we create a dummy
            # that will be removed when the node is expanded for the first
            # time.
            cnid._dummy = QtGui.QTreeWidgetItem(cnid)

            if node.can_auto_open( object ):
                cnid.setExpanded(True)

        # Return the newly created node:
        return cnid

    #---------------------------------------------------------------------------
    #  Deletes a specified tree node and all its children:
    #---------------------------------------------------------------------------

    def _delete_node ( self, nid ):
        """ Deletes a specified tree node and all its children.
        """
        for cnid in self._nodes_for( nid ):
            self._delete_node( cnid )

        pnid = nid.parent()
        if pnid is None:
            self._tree.takeTopLevelItem(self._tree.indexOfTopLevelItem(nid))
        else:
            if getattr(pnid, '_dummy', None) is not nid:
                expanded, node, object = self._get_node_data( nid )
                id_object   = id( object )
                object_info = self._map[ id_object ]
                for i, info in enumerate( object_info ):
                    if nid == info[1]:
                        del object_info[i]
                        break

                if len( object_info ) == 0:
                    self._remove_listeners( node, object )
                    del self._map[ id_object ]

            pnid.removeChild(nid)

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
            # Remove any dummy node.
            dummy = getattr(nid, '_dummy', None)
            if dummy is not None:
                nid.removeChild(dummy)
                del nid._dummy

            for child in node.get_children( object ):
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )

            # Indicate the item is now populated:
            self._set_node_data( nid, ( True, node, object) )

    #---------------------------------------------------------------------------
    #  Returns each of the child nodes of a specified node id:
    #---------------------------------------------------------------------------

    def _nodes_for ( self, nid ):
        """ Returns all child node ids of a specified node id.
        """
        return [nid.child(i) for i in range(nid.childCount())]

    #---------------------------------------------------------------------------
    #  Return the index of a specified node id within its parent:
    #---------------------------------------------------------------------------

    def _node_index ( self, nid ):
        pnid = nid.parent()
        if pnid is None:
            return ( None, None, None )

        for i in range(pnid.childCount()):
            if pnid.child(i) is nid:
                _, pnode, pobject = self._get_node_data( pnid )
                return ( pnode, pobject, i )

    #---------------------------------------------------------------------------
    #  Returns the icon index for the specified object:
    #---------------------------------------------------------------------------

    STD_ICON_MAP = {
        '<item>':   QtGui.QStyle.SP_FileIcon,
        '<group>':  QtGui.QStyle.SP_DirClosedIcon,
        '<open>':   QtGui.QStyle.SP_DirOpenIcon
    }

    def _get_icon ( self, node, object, is_expanded = False ):
        """ Returns the index of the specified object icon.
        """
        if not self.factory.show_icons:
            return QtGui.QIcon()

        icon_name = node.get_icon(object, is_expanded)
        if isinstance(icon_name, basestring):
            icon = self.STD_ICON_MAP.get(icon_name)

            if icon is not None:
                return self._tree.style().standardIcon(icon)

            path = node.get_icon_path( object )
            if isinstance( path, basestring ):
                path = [ path, node ]
            else:
                path.append( node )
            reference = resource_manager.locate_image( icon_name, path )
            if reference is None:
                return QtGui.QIcon()
            file_name = reference.filename
        else:
            # Assume it is an ImageResource, and get its file name directly:
            file_name = icon_name.absolute_path

        return QtGui.QIcon(pixmap_cache(file_name))

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

    def _object_info_for ( self, object, name = '' ):
        """ Returns the tree node data for a specified object as a list of the
            form: [ ( expanded, node, nid ), ... ].
        """
        result = []
        for name2, nid in self._map[ id( object ) ]:
            if name == name2:
                expanded, node, ignore = self._get_node_data( nid )
                result.append( ( expanded, node, nid ) )

        return result

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

    def _update_icon(self, nid):
        """ Updates the icon for a specified node.
        """
        expanded, node, object = self._get_node_data(nid)
        nid.setIcon(0, self._get_icon(node, object, expanded))

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
            editor.setWidget(None)
            editor._node_ui.dispose()
            editor._node_ui = editor._editor_nid = None

    #---------------------------------------------------------------------------
    #  Gets/Sets the node specific data:
    #---------------------------------------------------------------------------

    @staticmethod
    def _get_node_data(nid):
        """ Gets the node specific data. """
        return nid._py_data

    @staticmethod
    def _set_node_data(nid, data):
        """ Sets the node specific data. """
        nid._py_data = data

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
            pnid = nid.parent()
            if pnid is not self._tree.invisibleRootItem():
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
    #  Handles a tree node being expanded:
    #---------------------------------------------------------------------------

    def _on_item_expanded(self, nid):
        """ Handles a tree node being expanded.
        """
        expanded, node, object = self._get_node_data(nid)

        # If 'auto_close' requested for this node type, close all of the node's
        # siblings:
        if node.can_auto_close(object):
            parent = nid.parent()

            if parent is not None:
                for snid in self._nodes_for(parent):
                    if snid is not nid:
                        snid.setExpanded(False)

        # Expand the node (i.e. populate its children if they are not there
        # yet):
        self._expand_node(nid)

        self._update_icon(nid)

    #---------------------------------------------------------------------------
    #  Handles a tree node being collapsed:
    #---------------------------------------------------------------------------

    def _on_item_collapsed(self, nid):
        """ Handles a tree node being collapsed.
        """
        self._update_icon(nid)

    #---------------------------------------------------------------------------
    #  Handles a tree item click:
    #---------------------------------------------------------------------------

    def _on_item_clicked(self, nid, col):
        """ Handles a tree item being clicked.
        """
        _, node, object = self._get_node_data(nid)

        if node.click(object) is True and self.factory.on_click is not None:
            self.ui.evaluate(self.factory.on_click, object)

        # Fire the 'click' event with the object as its value:
        self.click = object

    #---------------------------------------------------------------------------
    #  Handles a tree item double click:
    #---------------------------------------------------------------------------

    def _on_item_dclicked(self, nid, col):
        """ Handles a tree item being double-clicked.
        """
        _, node, object = self._get_node_data(nid)

        if node.dclick(object) is True:
            if self.factory.on_dclick is not None:
                self.ui.evaluate(self.factory.on_dclick, object)
                self._veto = True
        else:
            self._veto = True

        # Fire the 'dclick' event with the clicked on object as value:
        self.dclick = object

    #---------------------------------------------------------------------------
    #  Handles a tree node being selected:
    #---------------------------------------------------------------------------

    def _on_tree_sel_changed(self):
        """ Handles a tree node being selected.
        """
        # Get the new selection:
        sel = self._tree.selectedItems()

        if len(sel) > 0:
            nid = sel[0]

            # If there is a real selection, get the associated object:
            expanded, node, object = self._get_node_data(nid)

            # Try to inform the node specific handler of the selection:
            not_handled = node.select(object)
        else:
            nid = None
            object = None
            not_handled = True

        # Set the value of the new selection:
        self._no_update_selected = True
        self.selected            = object
        self._no_update_selected = False

        # If no one has been notified of the selection yet, inform the editor's
        # select handler (if any) of the new selection:
        if not_handled is True:
            self.ui.evaluate(self.factory.on_select, object)

        # Check to see if there is an associated node editor pane:
        editor = self._editor
        if editor is not None:
            # If we already had a node editor, destroy it:
            editor.setUpdatesEnabled(False)
            self._clear_editor()

            # If there is a selected object, create a new editor for it:
            if object is not None:
                # Try to chain the undo history to the main undo history:
                view = node.get_view( object )
                if view is None:
                    view = object.trait_view()
                if (self.ui.history is not None) or (view.kind == 'subpanel'):
                    ui = object.edit_traits( parent = editor,
                                             view   = view,
                                             kind   = 'subpanel' )
                else:
                    # Otherwise, just set up our own new one:
                    ui = object.edit_traits( parent = editor,
                                             view   = view,
                                             kind   = 'panel' )


                # Make our UI the parent of the new UI:
                ui.parent = self.ui

                # Remember the new editor's UI and node info:
                editor._node_ui    = ui
                editor._editor_nid = nid

                # Finish setting up the editor:
                ui.control.layout().setMargin(0)
                editor.setWidget(ui.control)

            # Allow the editor view to show any changes that have occurred:
            editor.setUpdatesEnabled(True)

    #---------------------------------------------------------------------------
    #  Handles the user right clicking on a tree node:
    #---------------------------------------------------------------------------

    def _on_context_menu(self, pos):
        """ Handles the user requesting a context menuright clicking on a tree node.
        """
        nid = self._tree.itemAt(pos)

        if nid is None:
            return

        _, node, object = self._get_node_data(nid)

        self._data = (node, object, nid)
        self._context = {'object':  object,
                         'editor':  self,
                         'node':    node,
                         'info':    self.ui.info,
                         'handler': self.ui.handler}

        # Try to get the parent node of the node clicked on:
        pnid = nid.parent()
        if pnid is not self._tree.invisibleRootItem():
            _, parent_node, parent_object = self._get_node_data(pnid)
        else:
            parent_node = parent_object = None

        self._menu_node = node
        self._menu_parent_node = parent_node
        self._menu_parent_object = parent_object

        menu = node.get_menu(object)

        if menu is None:
            # Use the standard, default menu:
            menu = self._standard_menu(node, object)

        elif isinstance(menu, Menu):
            # Use the menu specified by the node:
            group = menu.find_group(NewAction)
            if group is not None:
                # Only set it the first time:
                group.id = ''
                actions  = self._new_actions( node, object )
                if len( actions ) > 0:
                    group.insert( 0, Menu( name = 'New', *actions ) )

        else:
            # All other values mean no menu should be displayed:
            menu = None

        # Only display the menu if a valid menu is defined:
        if menu is not None:
            qmenu = menu.create_menu( self._tree, self )
            qmenu.exec_(self._tree.mapToGlobal(pos))

        # Reset all menu related cached values:
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
        return self._menu_node.can_add(object, clipboard.instance_type)

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

        can_rename = (can_rename and self._menu_node.can_rename_me( object ))

        # Set the widget item's editable flag appropriately.
        nid = self._get_object_nid(object)
        flags = nid.flags()
        if can_rename:
            flags |= QtCore.Qt.ItemIsEditable
        else:
            flags &= ~QtCore.Qt.ItemIsEditable
        nid.setFlags(flags)

        return can_rename

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

    def perform ( self, action, action_event = None ):
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
        clipboard.instance = self._data[1]
        self._data = None

    #---------------------------------------------------------------------------
    #   Cuts the current tree node object into the paste buffer:
    #---------------------------------------------------------------------------

    def _menu_cut_node ( self ):
        """ Cuts the current tree node object into the paste buffer.
        """
        node, object, nid = self._data
        clipboard.instance = object
        self._data = None
        self._undoable_delete(*self._node_index(nid))

    #---------------------------------------------------------------------------
    #  Pastes the current contents of the paste buffer into the current node:
    #---------------------------------------------------------------------------

    def _menu_paste_node ( self ):
        """ Pastes the current contents of the paste buffer into the current
            node.
        """
        node, object, nid = self._data
        self._data = None
        self._undoable_append(node, object, clipboard.instance, False)

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
                    butn = QtGui.QMessageBox.question(
                                self._tree,
                                "Confirm Deletion",
                                "Are you sure you want to delete %s?" % node.get_label( object ),
                                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    if butn != QtGui.QMessageBox.Yes:
                        return

            self._undoable_delete( *self._node_index( nid ) )

    #---------------------------------------------------------------------------
    #  Renames the current tree node:
    #---------------------------------------------------------------------------

    def _menu_rename_node ( self ):
        """ Rename the current node.
        """
        _, _, nid = self._data
        self._data = None
        self._tree.editItem(nid)

    def _on_nid_changed(self, nid, col):
        """ Handle changes to a widget item.
        """
        # The node data may not have been set up for the nid yet.  Ignore it if
        # it hasn't.
        try:
            _, node, object = self._get_node_data(nid)
        except:
            return

        new_label = unicode(nid.text(col))
        old_label = node.get_label(object)

        if new_label != old_label:
            if new_label != '':
                node.set_label(object, new_label)
            else:
                nid.setText(col, old_label)

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
                self._tree.setCurrentItem(nid.child(nid.childCount() - 1))

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
            for cnid in self._nodes_for( nid ):
                self._delete_node( cnid )

            # Add all of the children back in as new nodes:
            for child in children:
                child, child_node = self._node_for( child )
                if child_node is not None:
                    self._append_node( nid, child_node, child )

        # Try to expand the node (if requested):
        if node.can_auto_open( object ):
            nid.setExpanded(True)

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
        start = event.index
        n     = len( event.added )
        end   = start + len( event.removed )
        tree                = self._tree

        for expanded, node, nid in self._object_info_for( object, name ):
            children = node.get_children( object )

            # If the new children aren't all at the end, remove/add them all:
            if (n > 0) and ((start + n) != len( children )):
                self._children_replaced( object, name, event )
                return

            # Only add/remove the changes if the node has already been expanded:
            if expanded:
                # Remove all of the children that were deleted:
                for cnid in self._nodes_for( nid )[ start: end ]:
                    self._delete_node( cnid )

                # Add all of the children that were added:
                for child in event.added:
                    child, child_node = self._node_for( child )
                    if child_node is not None:
                        self._append_node( nid, child_node, child )

            # Try to expand the node (if requested):
            if node.can_auto_open( object ):
                nid.setExpanded(True)

    #---------------------------------------------------------------------------
    #   Handles the label of an object being changed:
    #---------------------------------------------------------------------------

    def _label_updated ( self, object, name, label ):
        """  Handles the label of an object being changed.
        """
        # Prevent the itemChanged() signal from being emitted.
        blk = self._tree.blockSignals(True)

        nids = {}
        for name2, nid in self._map[ id( object ) ]:
            if nid not in nids:
                nids[ nid ] = None
                node = self._get_node_data( nid )[1]
                nid.setText(0, node.get_label(object))
                self._update_icon(nid)

        self._tree.blockSignals(blk)

#-- UI preference save/restore interface ---------------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if isinstance(self.control, QtGui.QSplitter):
            if isinstance(prefs, dict):
                structure = prefs.get('structure')
            else:
                structure = prefs

            self.control.restoreState(structure)

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        if isinstance(self.control, QtGui.QSplitter):
            return {'structure': str(self.control.saveState())}

        return None

#-- End UI preference save/restore interface -----------------------------------

#-------------------------------------------------------------------------------
#  '_TreeWidget' class:
#-------------------------------------------------------------------------------

class _TreeWidget(QtGui.QTreeWidget):
    """ The _TreeWidget class is a specialised QTreeWidget that reimplements
        the drag'n'drop support so that it hooks into the provided Traits
        support.
    """
    def __init__(self, editor, parent=None):
        """ Initialise the tree widget.
        """
        QtGui.QTreeWidget.__init__(self, parent)

        self.header().hide()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        self.connect(self, QtCore.SIGNAL('itemExpanded(QTreeWidgetItem *)'),
                editor._on_item_expanded)
        self.connect(self, QtCore.SIGNAL('itemCollapsed(QTreeWidgetItem *)'),
                editor._on_item_collapsed)
        self.connect(self,
                QtCore.SIGNAL('itemClicked(QTreeWidgetItem *, int)'),
                editor._on_item_clicked)
        self.connect(self,
                QtCore.SIGNAL('itemDoubleClicked(QTreeWidgetItem *, int)'),
                editor._on_item_dclicked)
        self.connect(self, QtCore.SIGNAL('itemSelectionChanged()'),
                editor._on_tree_sel_changed)
        self.connect(self, QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
                editor._on_context_menu)
        self.connect(self,
                QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'),
                editor._on_nid_changed)

        self._editor = editor
        self._dragging = None

    def startDrag(self, actions):
        """ Reimplemented to start the drag of a tree widget item.
        """
        nid = self.currentItem()
        if nid is None:
            return

        self._dragging = nid

        _, node, object = self._editor._get_node_data(nid)

        # Convert the item being dragged to MIME data.
        md = PyMimeData(node.get_drag_object(object))

        # Render the item being dragged as a pixmap.
        nid_rect = self.visualItemRect(nid)
        rect = nid_rect.intersected(self.viewport().rect())

        pm = QtGui.QPixmap(rect.size())
        pm.fill(self.palette().base().color())

        painter = QtGui.QPainter(pm)

        option = self.viewOptions()
        option.state |= QtGui.QStyle.State_Selected
        option.rect = QtCore.QRect(nid_rect.topLeft() - rect.topLeft(), nid_rect.size())

        self.itemDelegate().paint(painter, option, self.indexFromItem(nid))

        painter.end()

        # Calculate the hotspot so that the pixmap appears on top of the
        # original item.
        rect.adjust(self.horizontalOffset(), self.verticalOffset(), 0, 0)
        hspos = self.mapFromGlobal(QtGui.QCursor.pos()) - rect.topLeft()

        # Start the drag.
        drag = QtGui.QDrag(self)
        drag.setMimeData(md)
        drag.setPixmap(pm)
        drag.setHotSpot(hspos)
        drag.exec_(actions)

    def dragEnterEvent(self, e):
        """ Reimplemented to see if the current drag can be handled by the
            tree.
        """
        # Assume the drag is invalid.
        e.ignore()

        # Check what is being dragged.
        md = PyMimeData.coerce(e.mimeData())
        if md is None:
            return

        # We might be able to handle it (but it depends on what the final
        # target is).
        e.acceptProposedAction()

    def dragMoveEvent(self, e):
        """ Reimplemented to see if the current drag can be handled by the
            particular tree widget item underneath the cursor.
        """
        # Assume the drag is invalid.
        e.ignore()

        # Get the tree widget item under the cursor.
        nid = self.itemAt(e.pos())
        if nid is None:
            return

        # Check that the target is not the source of a child of the source.
        if self._dragging is not None:
            pnid = nid
            while pnid is not None:
                if pnid is self._dragging:
                    return

                pnid = pnid.parent()

        # A copy action is interpreted as moving the source to a particular
        # place within the target's parent.  A move action is interpreted as
        # moving the source to be a child of the target.
        if e.proposedAction() == QtCore.Qt.CopyAction:
            node, object, _ = self._editor._node_index(nid)
            insert = True
        else:
            _, node, object = self._editor._get_node_data(nid)
            insert = False

        # See if the model will accept a drop.
        data = PyMimeData.coerce(e.mimeData()).instance()

        if not node._is_droppable(object, data, insert):
            return

        e.acceptProposedAction()

    def dropEvent(self, e):
        """ Reimplemented to update the model and tree.
        """
        # Assume the drop is invalid.
        e.ignore()

        dragging = self._dragging
        self._dragging = None

        # Get the tree widget item under the cursor.
        nid = self.itemAt(e.pos())
        if nid is None:
            return

        # Get the data being dropped.
        data = PyMimeData.coerce(e.mimeData()).instance()

        editor = self._editor
        _, node, object = editor._get_node_data(nid)

        if e.proposedAction() == QtCore.Qt.MoveAction:
            if not node._is_droppable( object, data, False ):
                return

            if dragging is not None:
                data = node._drop_object( object, data, False )
                if data is not None:
                    try:
                        editor._begin_undo()
                        editor._undoable_delete(
                                 *editor._node_index( dragging ) )
                        editor._undoable_append( node, object, data, False )
                    finally:
                        editor._end_undo()
            else:
                data = node._drop_object( object, data )
                if data is not None:
                    editor._undoable_append( node, object, data )
        else:
            to_node, to_object, to_index = editor._node_index( nid )
            if to_node is not None:
                if dragging is not None:
                    data = node._drop_object( to_object, data, False )
                    if data is not None:
                        from_node, from_object, from_index = \
                            editor._node_index( dragging )
                        if ((to_object is from_object) and
                            (to_index > from_index)):
                            to_index -= 1
                        try:
                            editor._begin_undo()
                            editor._undoable_delete( from_node, from_object,
                                                   from_index )
                            editor._undoable_insert( to_node, to_object, to_index,
                                                   data, False )
                        finally:
                            editor._end_undo()
                else:
                    data = to_node._drop_object( to_object, data )
                    if data is not None:
                        editor._undoable_insert( to_node, to_object, to_index,
                                               data )

        e.acceptProposedAction()
