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

""" Defines the UI class used to represent an active traits-based user
    interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

import shelve
import os

from ..api import (Any, Bool, Callable, DictStrAny, Event, HasPrivateTraits,
    Instance, Int, List, Property, Str, TraitError, on_trait_change,
    property_depends_on)

from ..trait_base import traits_home, is_str

from .editor import Editor

from .view_elements import ViewElements

from .handler import Handler, ViewHandler

from .toolkit import toolkit

from .ui_info import UIInfo

from .item import Item

from .group import Group, ShadowGroup

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of **kind** types for views that must have a **parent** window specified
kind_must_have_parent = ( 'panel', 'subpanel' )

#-------------------------------------------------------------------------------
#  'UI' class:
#-------------------------------------------------------------------------------

class UI ( HasPrivateTraits ):
    """ Information about the user interface for a View.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The ViewElements object from which this UI resolves Include items
    view_elements = Instance( ViewElements )

    # Context objects that the UI is editing
    context = DictStrAny

    # Handler object used for event handling
    handler = Instance( Handler )

    # View template used to construct the user interface
    view = Instance( 'enthought.traits.ui.view.View' )

    # Panel or dialog associated with the user interface
    control = Any

    # The parent UI (if any) of this UI
    parent = Instance( 'UI' )

    # Toolkit-specific object that "owns" **control**
    owner = Any

    # UIInfo object containing context or editor objects
    info = Instance( UIInfo )

    # Result from a modal or wizard dialog:
    result = Bool( False )

    # Undo and Redo history
    history = Any

    # The KeyBindings object (if any) for this UI:
    key_bindings = Property # Instance( KeyBindings )

    # The unique ID for this UI for persistence
    id = Str

    # Have any modifications been made to UI contents?
    modified = Bool( False )

    # Event when the user interface has changed
    updated = Event( Bool )

    # Title of the dialog, if any
    title = Str

    # The ImageResource of the icon, if any
    icon = Any

    # Should the created UI have scroll bars?
    scrollable = Bool( False )

    # The number of currently pending editor error conditions
    errors = Int

    # The code used to rebuild an updated user interface
    rebuild = Callable

    #-- Private Traits ---------------------------------------------------------

    # Original context when used with a modal dialog
    _context = DictStrAny

    # Copy of original context used for reverting changes
    _revert = DictStrAny

    # List of methods to call once the user interface is created
    _defined = List

    # List of (visible_when,Editor) pairs
    _visible = List

    # List of (enabled_when,Editor) pairs
    _enabled = List

    # List of (checked_when,Editor) pairs
    _checked = List

    # Search stack used while building a user interface
    _search = List

    # List of dispatchable Handler methods
    _dispatchers = List

    # List of editors used to build the user interface
    _editors = List

    # List of names bound to the **info** object
    _names = List

    # Index of currently the active group in the user interface
    _active_group = Int

    # List of top-level groups used to build the user interface
    _groups = Property
    _groups_cache = Any

    # Count of levels of nesting for undoable actions
    _undoable = Int( -1 )

    # Code used to rebuild an updated user interface
    _rebuild = Callable

    # The statusbar listeners that have been set up:
    _statusbar = List

    # Does the UI contain any scrollable widgets?
    #
    # The _scrollable trait is set correctly, but not used currently because
    # its value is arrived at too late to be of use in building the UI.
    _scrollable = Bool( False )

    # List of traits that are reset when a user interface is recycled
    # (i.e. rebuilt).
    recyclable_traits = [
        '_context', '_revert', '_defined', '_visible', '_enabled', '_checked',
        '_search', '_dispatchers', '_editors', '_names', '_active_group',
        '_undoable', '_rebuild', '_groups_cache'
    ]

    # List of additional traits that are discarded when a user interface is
    # disposed.
    disposable_traits = [
        'view_elements', 'info', 'handler', 'context', 'view', 'history',
        'key_bindings', 'icon', 'rebuild',
    ]

    #---------------------------------------------------------------------------
    #  Initializes the traits object:
    #---------------------------------------------------------------------------

    def traits_init ( self ):
        """ Initializes the traits object.
        """
        self.info = UIInfo( ui = self )
        self.handler.init_info( self.info )

    #---------------------------------------------------------------------------
    #  Creates a user interface from the associated View template object:
    #---------------------------------------------------------------------------

    def ui ( self, parent, kind ):
        """ Creates a user interface from the associated View template object.
        """
        if (parent is None) and (kind in kind_must_have_parent):
            kind = 'live'
        self.view.on_trait_change( self._updated_changed, 'updated',
                                   dispatch = 'ui' )
        self.rebuild = getattr( toolkit(), 'ui_' + kind )
        self.rebuild( self, parent )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of a user interface:
    #---------------------------------------------------------------------------

    def dispose ( self, result = None, abort = False ):
        """ Disposes of the contents of a user interface.
        """
        if result is not None:
            self.result = result

        # Only continue if the view has not already been disposed of:
        if self.control is not None:
            # Save the user preference information for the user interface:
            if not abort:
                self.save_prefs()

            # Finish disposing of the user interface:
            self.finish()

    #---------------------------------------------------------------------------
    #  Recycles the user interface prior to rebuilding it:
    #---------------------------------------------------------------------------

    def recycle ( self ):
        """ Recycles the user interface prior to rebuilding it.
        """
        # Reset all user interface editors:
        self.reset( destroy = False )

        # Discard any context object associated with the ui view control:
        self.control._object = None

        # Reset all recyclable traits:
        self.reset_traits( self.recyclable_traits )

    #---------------------------------------------------------------------------
    #  Finishes a user interface:
    #---------------------------------------------------------------------------

    def finish ( self ):
        """ Finishes disposing of a user interface.
        """
        # Reset the contents of the user interface:
        self.reset( destroy = False )

        # Make sure that 'visible', 'enabled', and 'checked' handlers are not
        # called after the editor has been disposed:
        for object in self.context.values():
            object.on_trait_change( self._evaluate_when, remove = True )

        # Notify the handler that the view has been closed:
        self.handler.closed( self.info, self.result )

        # Clear the back-link from the UIInfo object to us:
        self.info.ui = None

        # Destroy the view control:
        self.control._object = None
        toolkit().destroy_control( self.control )
        self.control = None

        # Dispose of any KeyBindings object we reference:
        self.key_bindings.dispose()

        # Break the linkage to any objects in the context dictionary:
        self.context.clear()

        # Remove specified symbols from our dictionary to aid in clean-up:
        self.reset_traits( self.recyclable_traits )
        self.reset_traits( self.disposable_traits )

    #---------------------------------------------------------------------------
    #  Resets the contents of the user interface:
    #---------------------------------------------------------------------------

    def reset ( self, destroy = True ):
        """ Resets the contents of a user interface.
        """
        for editor in self._editors:
            if editor._ui is not None:
                # Propagate result to enclosed ui objects:
                editor._ui.result = self.result
            editor.dispose()

            # Zap the control. If there are pending events for the control in
            # the UI queue, the editor's '_update_editor' method will see that
            # the control is None and discard the update request:
            editor.control = None

        # Remove any statusbar listeners that have been set up:
        for object, handler, name in self._statusbar:
            object.on_trait_change( handler, name, remove = True )

        del self._statusbar[:]

        if destroy:
            toolkit().destroy_children( self.control )

        for dispatcher in self._dispatchers:
            dispatcher.remove()

    #---------------------------------------------------------------------------
    #  Find the definition of the specified Include object in the current user
    #  interface building context:
    #---------------------------------------------------------------------------

    def find ( self, include ):
        """ Finds the definition of the specified Include object in the current
            user interface building context.
        """
        context = self.context
        result  = None

        # Get the context 'object' (if available):
        if len( context ) == 1:
            object = context.values()[0]
        else:
            object = context.get( 'object' )

        # Try to use our ViewElements objects:
        ve = self.view_elements

        # If none specified, try to get it from the UI context:
        if (ve is None) and (object is not None):
            # Use the context object's ViewElements (if available):
            ve = object.trait_view_elements()

        # Ask the ViewElements to find the requested item for us:
        if ve is not None:
            result = ve.find( include.id, self._search )

        # If not found, then try to search the 'handler' and 'object' for a
        # method we can call that will define it:
        if result is None:
            handler = context.get( 'handler' )
            if handler is not None:
                method = getattr( handler, include.id, None )
                if callable( method ):
                    result = method()

            if (result is None) and (object is not None):
                method = getattr( object, include.id, None )
                if callable( method ):
                    result = method()

        return result

    #---------------------------------------------------------------------------
    #  Returns the current search stack level:
    #---------------------------------------------------------------------------

    def push_level ( self ):
        """ Returns the current search stack level.
        """
        return len( self._search )

    #---------------------------------------------------------------------------
    #  Restores a previously pushed search stack level:
    #---------------------------------------------------------------------------

    def pop_level ( self, level ):
        """ Restores a previously pushed search stack level.
        """
        del self._search[ : len( self._search ) - level ]

    #---------------------------------------------------------------------------
    #  Performs all post user interface creation processing:
    #---------------------------------------------------------------------------

    def prepare_ui ( self ):
        """ Performs all processing that occurs after the user interface is
            created.
        """
        # Invoke all of the editor 'name_defined' methods we've accumulated:
        info = self.info.set( initialized = False )
        for method in self._defined:
            method( info )

        # Then reset the list, since we don't need it anymore:
        del self._defined[:]

        # Synchronize all context traits with associated editor traits:
        self.sync_view()

        # Hook all keyboard events:
        toolkit().hook_events( self, self.control, 'keys', self.key_handler )

        # Hook all events if the handler is an extended 'ViewHandler':
        handler = self.handler
        if isinstance( handler, ViewHandler ):
            toolkit().hook_events( self, self.control )

        # Invoke the handler's 'init' method, and abort if it indicates failure:
        if handler.init( info ) == False:
            raise TraitError, 'User interface creation aborted'

        # For each Handler method whose name is of the form
        # 'object_name_changed', where 'object' is the name of an object in the
        # UI's 'context', create a trait notification handler that will call
        # the method whenever 'object's 'name' trait changes. Also invoke the
        # method immediately so initial user interface state can be correctly
        # set:
        context = self.context
        for name in self._each_trait_method( handler ):
            if name[-8:] == '_changed':
                prefix = name[:-8]
                col    = prefix.find( '_', 1 )
                if col >= 0:
                    object = context.get( prefix[ : col ] )
                    if object is not None:
                        method     = getattr( handler, name )
                        trait_name = prefix[ col + 1: ]
                        self._dispatchers.append( Dispatcher(
                             method, info, object, trait_name ) )
                        if object.base_trait( trait_name ).type != 'event':
                            method( info )

        # If there are any Editor object's whose 'visible', 'enabled' or
        # 'checked' state is controlled by a 'visible_when', 'enabled_when' or
        # 'checked_when' expression, set up an 'anytrait' changed notification
        # handler on each object in the 'context' that will cause the 'visible',
        # 'enabled' or 'checked' state of each affected Editor to be set. Also
        # trigger the evaluation immediately, so the visible, enabled or checked
        # state of each Editor can be correctly initialized:
        if (len( self._visible ) +
            len( self._enabled ) +
            len( self._checked )) > 0:
            for object in context.values():
                object.on_trait_change( self._evaluate_when, dispatch = 'ui' )
            self._evaluate_when()

        # Indicate that the user interface has been initialized:
        info.initialized = True

    #---------------------------------------------------------------------------
    #  Synchronize context object traits with view editor traits:
    #---------------------------------------------------------------------------

    def sync_view ( self ):
        """ Synchronize context object traits with view editor traits.
        """
        for name, object in self.context.items():
            self._sync_view( name, object, 'sync_to_view',   'from' )
            self._sync_view( name, object, 'sync_from_view', 'to'   )
            self._sync_view( name, object, 'sync_with_view', 'both' )

    def _sync_view ( self, name, object, metadata, direction ):
        info = self.info
        for trait_name, trait in object.traits( **{metadata: is_str} ).items():
            for sync in getattr( trait, metadata ).split( ',' ):
                try:
                    editor_id, editor_name = [ item.strip()
                                               for item in sync.split( '.' ) ]
                except:
                    raise TraitError( "The '%s' metadata for the '%s' trait in "
                        "the '%s' context object should be of the form: "
                        "'id1.trait1[,...,idn.traitn]." %
                        ( metadata, trait_name, name ) )

                editor = getattr( info, editor_id, None )
                if editor is not None:
                    editor.sync_value( '%s.%s' % ( name, trait_name ),
                                       editor_name, direction )
                else:
                    raise TraitError( "No editor with id = '%s' was found for "
                        "the '%s' metadata for the '%s' trait in the '%s' "
                        "context object." %
                        ( editor_id,metadata, trait_name, name ) )

    #---------------------------------------------------------------------------
    #  Gets the current value of a specified extended trait name:
    #---------------------------------------------------------------------------

    def get_extended_value ( self, name ):
        """ Gets the current value of a specified extended trait name.
        """
        names = name.split( '.' )
        if len( names ) > 1:
            value = self.context[ names[0] ]
            del names[0]
        else:
            value = self.context[ 'object' ]

        for name in names:
            value = getattr( value, name )

        return value

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the UI:
    #---------------------------------------------------------------------------

    def restore_prefs ( self ):
        """ Retrieves and restores any saved user preference information
        associated with the UI.
        """
        id = self.id
        if id != '':
            db = self.get_ui_db()
            if db is not None:
                try:
                    ui_prefs = db.get( id )
                    db.close()
                    return self.set_prefs( ui_prefs )
                except:
                    pass

        return None

    #---------------------------------------------------------------------------
    #  Restores user preference information for the UI:
    #---------------------------------------------------------------------------

    def set_prefs ( self, prefs ):
        """ Sets the values of user preferences for the UI.
        """
        if isinstance( prefs, dict ):
            info = self.info
            for name in self._names:
                editor = getattr( info, name, None )
                if isinstance( editor, Editor ) and (editor.ui is self):
                    editor_prefs = prefs.get( name )
                    if editor_prefs != None:
                        editor.restore_prefs( editor_prefs )

            if self.key_bindings is not None:
                key_bindings = prefs.get( '$' )
                if key_bindings is not None:
                    self.key_bindings.merge( key_bindings )

            return prefs.get( '' )

        return None

    #---------------------------------------------------------------------------
    #  Saves any user preference information associated with the UI:
    #---------------------------------------------------------------------------

    def save_prefs ( self, prefs = None ):
        """ Saves any user preference information associated with the UI.
        """
        if prefs is None:
            toolkit().save_window( self )
            return

        id = self.id
        if id != '':
            db = self.get_ui_db( mode = 'c' )
            if db is not None:
                db[ id ] = self.get_prefs( prefs )
                db.close()

    #---------------------------------------------------------------------------
    #  Gets the preferences to be saved for the user interface:
    #---------------------------------------------------------------------------

    def get_prefs ( self, prefs = None ):
        """ Gets the preferences to be saved for the user interface.
        """
        ui_prefs = {}
        if prefs is not None:
            ui_prefs[''] = prefs

        if self.key_bindings is not None:
            ui_prefs['$'] = self.key_bindings

        info = self.info
        for name in self._names:
            editor = getattr( info, name, None )
            if isinstance( editor, Editor ) and (editor.ui is self):
                prefs = editor.save_prefs()
                if prefs != None:
                    ui_prefs[ name ] = prefs

        return ui_prefs

    #---------------------------------------------------------------------------
    #  Gets a reference to the traits UI preference database:
    #---------------------------------------------------------------------------

    def get_ui_db ( self, mode = 'r' ):
        """ Returns a reference to the Traits UI preference database.
        """
        try:
            return shelve.open( os.path.join( traits_home(), 'traits_ui' ),
                                flag = mode, protocol = -1 )
        except:
            return None

    #---------------------------------------------------------------------------
    #  Returns a list of editors for the given trait name.
    #---------------------------------------------------------------------------

    def get_editors ( self, name ):
        """ Returns a list of editors for the given trait name.
        """
        return [ editor for editor in self._editors if editor.name == name ]

    #---------------------------------------------------------------------------
    #  Returns the list of editor error controls contained by the user
    #  interface:
    #---------------------------------------------------------------------------

    def get_error_controls ( self ):
        """ Returns the list of editor error controls contained by the user
            interface.
        """
        controls = []
        for editor in self._editors:
            control = editor.get_error_control()
            if isinstance( control, list ):
                controls.extend( control )
            else:
                controls.append( control )

        return controls

    #---------------------------------------------------------------------------
    #  Adds a Handler method to the list of methods to be called once the user
    #  interface has been constructed:
    #---------------------------------------------------------------------------

    def add_defined ( self, method ):
        """ Adds a Handler method to the list of methods to be called once the
            user interface has been constructed.
        """
        self._defined.append( method )

    #---------------------------------------------------------------------------
    #  Add's a conditionally enabled Editor object to the list of monitored
    #  'visible_when' objects:
    #---------------------------------------------------------------------------

    def add_visible ( self, visible_when, editor ):
        """ Adds a conditionally enabled Editor object to the list of monitored
            'visible_when' objects.
        """
        try:
            self._visible.append( ( compile( visible_when, '<string>', 'eval' ),
                                    editor ) )
        except:
            pass
            # fixme: Log an error here...

    #---------------------------------------------------------------------------
    #  Add's a conditionally enabled Editor object to the list of monitored
    #  'enabled_when' objects:
    #---------------------------------------------------------------------------

    def add_enabled ( self, enabled_when, editor ):
        """ Adds a conditionally enabled Editor object to the list of monitored
            'enabled_when' objects.
        """
        try:
            self._enabled.append( ( compile( enabled_when, '<string>', 'eval' ),
                                    editor ) )
        except:
            pass
            # fixme: Log an error here...

    #---------------------------------------------------------------------------
    #  Add's a conditionally checked (menu/toolbar) Editor object to the list of
    #  monitored 'checked_when' objects:
    #---------------------------------------------------------------------------

    def add_checked ( self, checked_when, editor ):
        """ Adds a conditionally enabled (menu) Editor object to the list of
            monitored 'checked_when' objects.
        """
        try:
            self._checked.append( ( compile( checked_when, '<string>', 'eval' ),
                                    editor ) )
        except:
            pass
            # fixme: Log an error here...

    #---------------------------------------------------------------------------
    #  Performs an 'undoable' action:
    #---------------------------------------------------------------------------

    def do_undoable ( self, action, *args, **kw ):
        """ Performs an action that can be undone.
        """
        undoable = self._undoable
        try:
            if (undoable == -1) and (self.history is not None):
                self._undoable = self.history.now

            action( *args, **kw )
        finally:
            if undoable == -1:
                self._undoable = -1

    #---------------------------------------------------------------------------
    #  Routes a 'hooked' event to the correct handler method:
    #---------------------------------------------------------------------------

    def route_event ( self, event ):
        """ Routes a "hooked" event to the correct handler method.
        """
        toolkit().route_event( self, event )

    #---------------------------------------------------------------------------
    #  Handles key events when the view has a set of KeyBindings:
    #---------------------------------------------------------------------------

    def key_handler ( self, event, skip = True ):
        """ Handles key events.
        """
        key_bindings = self.key_bindings
        handled      = ((key_bindings is not None) and
                         key_bindings.do( event, [], self.info,
                                          recursive = (self.parent is None) ))

        if (not handled) and (self.parent is not None):
            handled = self.parent.key_handler( event, False )

        if (not handled) and skip:
            toolkit().skip_event(event)

        return handled

    #---------------------------------------------------------------------------
    #  Evaluates a specified function in the UI's context:
    #---------------------------------------------------------------------------

    def evaluate ( self, function, *args, **kw_args ):
        """ Evaluates a specified function in the UI's **context**.
        """
        if function is None:
            return None

        if callable( function ):
            return function( *args, **kw_args )

        context = self.context.copy()
        context[ 'ui' ]      = self
        context[ 'handler' ] = self.handler
        return eval( function, globals(), context )( *args, **kw_args )

    #---------------------------------------------------------------------------
    #  Evaluates an expression in the UI's 'context' and returns the result:
    #---------------------------------------------------------------------------

    def eval_when ( self, when, result = True ):
        """ Evaluates an expression in the UI's **context** and returns the
            result.
        """
        context = self._get_context( self.context )
        try:
            result = eval( when, globals(), context )
        except:
            # fixme: Should the exception be logged somewhere?
            pass

        del context[ 'ui' ]

        return result

    #---------------------------------------------------------------------------
    #  Gets the context to use for evaluating an expression:
    #---------------------------------------------------------------------------

    def _get_context ( self, context ):
        """ Gets the context to use for evaluating an expression.
        """
        name = 'object'
        n    = len( context )
        if (n == 2) and ('handler' in context):
            for name, value in context.items():
                if name != 'handler':
                    break
        elif n == 1:
            name = context.keys()[0]

        value = context.get( name )
        if value is not None:
            context2 = value.trait_get()
            context2.update( context )
        else:
            context2 = context.copy()

        context2['ui'] = self

        return context2

    #---------------------------------------------------------------------------
    #  Sets the 'visible', 'enabled' and/or 'checked' state for all Editors
    #  controlled by a 'visible_when', 'enabled_when' or 'checked_when'
    #  expression:
    #---------------------------------------------------------------------------

    def _evaluate_when ( self ):
        """ Sets the 'visible', 'enabled', and 'checked' states for all Editors
            controlled by a 'visible_when', 'enabled_when' or 'checked_when'
            expression.
        """
        self._evaluate_condition( self._visible, 'visible' )
        self._evaluate_condition( self._enabled, 'enabled' )
        self._evaluate_condition( self._checked, 'checked' )

    #---------------------------------------------------------------------------
    #  Evaluates a list of ( eval, editor ) pairs and sets a specified trait on
    #  each editor to reflect the boolean truth of the expression evaluated:
    #---------------------------------------------------------------------------

    def _evaluate_condition ( self, conditions, trait ):
        """ Evaluates a list of (eval,editor) pairs and sets a specified trait
        on each editor to reflect the Boolean value of the expression.
        """
        context = self._get_context( self.context )
        for when, editor in conditions:
            value = True
            try:
                if not eval( when, globals(), context ):
                    value = False
            except:
                # fixme: Should the exception be logged somewhere?
                pass

            setattr( editor, trait, value )

    #---------------------------------------------------------------------------
    #  Implementation of the '_groups' property:
    #  (Returns the top-level Groups for the view (after resolving Includes))
    #---------------------------------------------------------------------------

    def _get__groups ( self ):
        """ Returns the top-level Groups for the view (after resolving
        Includes. (Implements the **_groups** property.)
        """
        if self._groups_cache is None:
            shadow_group       = self.view.content.get_shadow( self )
            self._groups_cache = shadow_group.get_content()
            for item in self._groups_cache:
                if isinstance( item, Item ):
                    self._groups_cache = [
                        ShadowGroup( shadow  = Group( *self._groups_cache ),
                                     content = self._groups_cache,
                                     groups  = 1 )
                    ]
                    break
        return self._groups_cache

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'view, context' )
    def _get_key_bindings ( self ):
        view, context = self.view, self.context
        if (view is None) or (context is None):
            return None

        # Get the KeyBindings object to use:
        values       = context.values()
        key_bindings = view.key_bindings
        if key_bindings is None:
            from .key_bindings import KeyBindings

            return KeyBindings( controllers = values)

        return key_bindings.clone( controllers = values )

    #-- Traits Event Handlers --------------------------------------------------

    def _updated_changed ( self ):
        if self.rebuild is not None:
            toolkit().rebuild_ui( self )

    def _title_changed ( self ):
        if self.control is not None:
            toolkit().set_title( self )

    def _icon_changed ( self ):
        if self.control is not None:
            toolkit().set_icon( self )

    @on_trait_change( 'parent, view, context' )
    def _pvc_changed ( self ):
        parent = self.parent
        if (parent is not None) and (self.key_bindings is not None):
            # If we don't have our own history, use our parent's:
            if self.history is None:
                self.history = parent.history

            # Link our KeyBindings object as a child of our parent's
            # KeyBindings object (if any):
            if parent.key_bindings is not None:
                parent.key_bindings.children.append( self.key_bindings )

#-------------------------------------------------------------------------------
#  'Dispatcher' class:
#-------------------------------------------------------------------------------

class Dispatcher ( object ):

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, method, info, object, method_name ):
        """ Initializes the object.
        """
        self.method      = method
        self.info        = info
        self.object      = object
        self.method_name = method_name
        object.on_trait_change( self.dispatch, method_name, dispatch = 'ui' )

    #---------------------------------------------------------------------------
    #  Dispatches the method:
    #---------------------------------------------------------------------------

    def dispatch ( self ):
        """ Dispatches the method.
        """
        self.method( self.info )

    #---------------------------------------------------------------------------
    #  Remove the dispatcher:
    #---------------------------------------------------------------------------

    def remove ( self ):
        """ Removes the dispatcher.
        """
        self.object.on_trait_change( self.dispatch, self.method_name,
                                     remove = True )

