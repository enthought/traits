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

""" Defines the abstract Editor class, which represents an editing control for
    an object trait in a Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import (Any, Bool, HasPrivateTraits, HasTraits, Instance, Property,
    ReadOnly, Str, Trait, TraitError, TraitListEvent, Undefined,
    cached_property)

from ..trait_base import not_none

from .editor_factory import EditorFactory

from .context_value import ContextValue

from .undo import UndoItem

from .item import Item

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Reference to an EditorFactory object
factory_trait = Trait( EditorFactory )

#-------------------------------------------------------------------------------
#  'Editor' abstract base class:
#-------------------------------------------------------------------------------

class Editor ( HasPrivateTraits ):
    """ Represents an editing control for an object trait in a Traits-based
        user interface.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The UI (user interface) this editor is part of:
    ui = Instance( 'enthought.traits.ui.ui.UI' )

    # Full name of the object the editor is editing (e.g. 'object.link1.link2'):
    object_name = Str( 'object' )

    # The object this editor is editing (e.g. object.link1.link2):
    object = Instance( HasTraits )

    # The name of the trait this editor is editing (e.g. 'value'):
    name = ReadOnly

    # The context object the editor is editing (e.g. object):
    context_object = Property

    # The extended name of the object trait being edited. That is,
    # 'object_name.name' minus the context object name at the beginning. For
    # example: 'link1.link2.value':
    extended_name = Property

    # Original value of object.name (e.g. object.link1.link2.value):
    old_value = Any

    # Text description of the object trait being edited:
    description = ReadOnly

    # The Item object used to create this editor:
    item = Instance( Item, () )

    # The GUI widget defined by this editor:
    control = Any

    # The GUI label (if any) defined by this editor:
    label_control = Any

    # Is the underlying GUI widget enabled?
    enabled = Bool( True )

    # Is the underlying GUI widget visible?
    visible = Bool( True )

    # Is the underlying GUI widget scrollable?
    scrollable = Bool( False )

    # The EditorFactory used to create this editor:
    factory = factory_trait

    # Is the editor updating the object.name value?
    updating = Bool( False )

    # Current value for object.name:
    value = Property

    # Current value of object trait as a string:
    str_value = Property

    # The trait the editor is editing (not its value, but the trait itself):
    value_trait = Property

    # The current editor invalid state status:
    invalid = Bool( False )

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, parent, **traits ):
        """ Initializes the editor object.
        """
        HasPrivateTraits.__init__( self, **traits )
        try:
            self.old_value = getattr( self.object, self.name )
        except AttributeError:
            # Getting the attribute will fail for 'Event' traits:
            self.old_value = Undefined

        # Synchronize the application invalid state status with the editor's:
        self.sync_value( self.factory.invalid, 'invalid', 'from' )

    #---------------------------------------------------------------------------
    #  Finishes editor set-up:
    #---------------------------------------------------------------------------

    def prepare ( self, parent ):
        """ Finishes setting up the editor.
        """
        name = self.extended_name
        if name != 'None':
            self.context_object.on_trait_change( self._update_editor, name,
                                                 dispatch = 'ui' )
        self.init( parent )
        self._sync_values()
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Assigns focus to the editor's underlying toolkit widget:
    #---------------------------------------------------------------------------
    
    def set_focus ( self ):
        """ Assigns focus to the editor's underlying toolkit widget.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.ui is None:
            return

        name = self.extended_name
        if name != 'None':
            self.context_object.on_trait_change( self._update_editor, name,
                                                 remove = True )

        if self._user_from is not None:
            for name, handler in self._user_from:
                self.on_trait_change( handler, name, remove = True )

        if self._user_to is not None:
            for object, name, handler in self._user_to:
                object.on_trait_change( handler, name, remove = True )

        # Break linkages to references we no longer need:
        self.object = self.ui = self.item = self.factory = self.control = \
        self.label_control = self.old_value = self._context_object = None

    #---------------------------------------------------------------------------
    #  Returns the context object the editor is using (Property implementation):
    #---------------------------------------------------------------------------

    @cached_property
    def _get_context_object ( self ):
        """ Returns the context object the editor is using (Property
            implementation).
        """
        object_name = self.object_name
        context_key = object_name.split( '.', 1 )[0]
        if (object_name != '') and (context_key in self.ui.context):
            return self.ui.context[ context_key ]

        # This handles the case of a 'ListItemProxy', which is not in the
        # ui.context, but is the editor 'object':
        return self.object

    #---------------------------------------------------------------------------
    #  Returns the extended trait name being edited (Property implementation):
    #---------------------------------------------------------------------------

    @cached_property
    def _get_extended_name ( self ):
        """ Returns the extended trait name being edited (Property
            implementation).
        """
        return ('%s.%s' % ( self.object_name, self.name )).split( '.', 1 )[1]

    #---------------------------------------------------------------------------
    #  Returns the trait the editor is editing (Property implementation):
    #---------------------------------------------------------------------------

    def _get_value_trait ( self ):
        """ Returns the trait the editor is editing (Property implementation).
        """
        return self.object.trait( self.name )

    #---------------------------------------------------------------------------
    #  Gets/Sets the associated object trait's value:
    #---------------------------------------------------------------------------

    def _get_value ( self ):
        return getattr( self.object, self.name, Undefined )

    def _set_value ( self, value ):
        if self.name != 'None':
            self.ui.do_undoable( self.__set_value, value )

    def __set_value ( self, value ):
        self._no_update = True
        try:
            try:
                handler  = self.ui.handler
                obj_name = self.object_name
                name     = self.name
                method   = (getattr( handler, '%s_%s_setattr' % ( obj_name,
                                              name ), None ) or
                            getattr( handler, '%s_setattr' % name, None ) or
                            getattr( handler, 'setattr' ))
                method( self.ui.info, self.object, name, value )
            except TraitError, excp:
                self.error( excp )
                raise
        finally:
            self._no_update = False

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified object trait value:
    #---------------------------------------------------------------------------

    def string_value ( self, value, format_func = None ):
        """ Returns the text representation of a specified object trait value.

            If the **format_func** attribute is set on the editor factory, then
            this method calls that function to do the formatting.  If the
            **format_str** attribute is set on the editor factory, then this
            method uses that string for formatting. If neither attribute is
            set, then this method just calls the built-in unicode() function.
        """
        factory = self.factory
        if factory.format_func is not None:
            return factory.format_func( value )

        if factory.format_str != '':
            return factory.format_str % value

        if format_func is not None:
            return format_func( value )

        return unicode( value )

    #---------------------------------------------------------------------------
    #  Returns the text representation of the object trait:
    #---------------------------------------------------------------------------

    def _get_str_value ( self ):
        """ Returns the text representation of the object trait.
        """
        return self.string_value( getattr( self.object, self.name, Undefined ) )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified value:
    #---------------------------------------------------------------------------

    def _str ( self, value ):
        """ Returns the text representation of a specified value.
        """
        # In Unicode!
        return unicode( value )

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #
    #  (Should normally be overridden in a subclass)
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass

    #---------------------------------------------------------------------------
    #  Performs updates when the object trait changes:
    #---------------------------------------------------------------------------

    def _update_editor ( self, object, name, old_value, new_value ):
        """ Performs updates when the object trait changes.
        """
        # If background threads have modified the trait the editor is bound to,
        # their trait notifications are queued to the UI thread. It is possible
        # that by the time the UI thread dispatches these events, the UI the
        # editor is part of has already been closed. So we need to check if we
        # are still bound to a live UI, and if not, exit immediately:
        if self.ui is None:
            return

        # If the notification is for an object different than the one actually
        # being edited, it is due to editing an item of the form:
        # object.link1.link2.name, where one of the 'link' objects may have
        # been modified. In this case, we need to rebind the current object
        # being edited:
        if object is not self.object:
            self.object = eval( self.object_name, globals(), self.ui.context )

        # If the editor has gone away for some reason, disconnect and exit:
        if self.control is None:
            self.context_object.on_trait_change( self._update_editor,
                                    self.extended_name, remove = True )
            return

        # Log the change that was made (as long as it is not for an event):
        if object.base_trait( name ).type != 'event':
            self.log_change( self.get_undo_item, object, name,
                                                 old_value, new_value )

        # If the change was not caused by the editor itself:
        if not self._no_update:
            # Update the editor control to reflect the current object state:
            self.update_editor()

    #---------------------------------------------------------------------------
    #  Logs a change made in the editor:
    #---------------------------------------------------------------------------

    def log_change ( self, undo_factory, *undo_args ):
        """ Logs a change made in the editor.
        """
        # Indicate that the contents of the user interface have been changed:
        ui          = self.ui
        ui.modified = True

        # Create an undo history entry if we are maintaining a history:
        undoable = ui._undoable
        if undoable >= 0:
            history = ui.history
            if history is not None:
                item = undo_factory( *undo_args )
                if item is not None:
                    if undoable == history.now:
                        # Create a new undo transaction:
                        history.add( item )
                    else:
                        # Extend the most recent undo transaction:
                        history.extend( item )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #
    #  (Should normally be overridden in a subclass)
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

    #---------------------------------------------------------------------------
    #  Creates an undo history entry:
    #
    #  (Can be overridden in a subclass for special value types)
    #---------------------------------------------------------------------------

    def get_undo_item ( self, object, name, old_value, new_value ):
        """ Creates an undo history entry.
        """
        return UndoItem( object    = object,
                         name      = name,
                         old_value = old_value,
                         new_value = new_value )

    #---------------------------------------------------------------------------
    #  Returns a tuple of the form ( context_object, name[.name...], callable )
    #  for a specified extended name of the form: name or
    #  context_object_name.name[.name...]:
    #---------------------------------------------------------------------------

    def parse_extended_name ( self, name ):
        """ Returns a tuple of the form ( context_object, 'name[.name...],
            callable ) for a specified extended name of the form: 'name' or
            'context_object_name.name[.name...]'.
        """
        col = name.find( '.' )
        if col < 0:
            object = self.context_object
        else:
            object, name = self.ui.context[ name[ : col ] ], name[ col + 1: ]

        return ( object, name, eval( "lambda obj=object: obj." + name ) )

    #---------------------------------------------------------------------------
    #  Initializes and synchronizes (as needed) editor traits with the value of
    #  corresponding factory traits:
    #---------------------------------------------------------------------------

    def _sync_values ( self ):
        """ Initializes and synchronizes (as needed) editor traits with the
            value of corresponding factory traits.
        """
        factory = self.factory
        for name, trait in factory.traits( sync_value = not_none ):
            value = getattr( factory, name )
            if isinstance( value, ContextValue ):
                self_trait = self.trait( name )
                self.sync_value( value.name, name,
                                 self_trait.sync_value or trait.sync_value,
                                 self_trait.is_list is True )
            elif value is not Undefined:
                setattr( self, name, value )

    #---------------------------------------------------------------------------
    #  Sets/Unsets synchronization between an editor trait and a user object
    #  trait:
    #---------------------------------------------------------------------------

    def sync_value ( self, user_name, editor_name, mode = 'both',
                           is_list = False ):
        """ Sets or unsets synchronization between an editor trait and a user
            object trait.
        """
        if user_name != '':
            key = '%s:%s' % ( user_name, editor_name )

            if self._no_trait_update is None:
                self._no_trait_update = {}

            user_ref = 'user_object'
            col      = user_name.find( '.' )
            if col < 0:
                user_object = self.context_object
                xuser_name  = user_name
            else:
                user_object = self.ui.context[ user_name[ : col ] ]
                user_name   = xuser_name = user_name[ col + 1: ]
                col         = user_name.rfind( '.' )
                if col >= 0:
                    user_ref += ('.' + user_name[ : col ])
                    user_name = user_name[ col + 1: ]

            user_value = compile( '%s.%s' % ( user_ref, user_name ),
                                  '<string>', 'eval' )
            user_ref   = compile( user_ref, '<string>', 'eval' )

            if mode in ( 'from', 'both' ):

                def user_trait_modified ( new ):
                    # Need this to include 'user_object' in closure:
                    user_object
                    if key not in self._no_trait_update:
                        self._no_trait_update[ key ] = None
                        try:
                            setattr( self, editor_name, new )
                        except:
                            pass
                        del self._no_trait_update[ key ]

                user_object.on_trait_change( user_trait_modified, xuser_name )

                if self._user_to is None:
                    self._user_to = []
                self._user_to.append( ( user_object, xuser_name,
                                        user_trait_modified ) )

                if is_list:

                    def user_list_modified ( event ):
                        if isinstance( event, TraitListEvent ):
                            if key not in self._no_trait_update:
                                self._no_trait_update[ key ] = None
                                n = event.index
                                try:
                                    getattr( self, editor_name )[
                                        n: n + len(event.removed)] = event.added
                                except:
                                    pass
                                del self._no_trait_update[ key ]

                    user_object.on_trait_change( user_list_modified,
                                    xuser_name + '_items' )
                    self._user_to.append( ( user_object, xuser_name + '_items',
                                            user_list_modified ) )

                try:
                    setattr( self, editor_name, eval( user_value ) )
                except:
                    pass

            if mode in ( 'to', 'both' ):

                def editor_trait_modified ( new ):
                    # Need this to include 'user_object' in closure:
                    user_object
                    if key not in self._no_trait_update:
                        self._no_trait_update[ key ] = None
                        try:
                            setattr( eval( user_ref ), user_name, new )
                        except:
                            pass
                        del self._no_trait_update[ key ]

                self.on_trait_change( editor_trait_modified, editor_name )

                if self._user_from is None:
                    self._user_from = []
                self._user_from.append( ( editor_name, editor_trait_modified ) )

                if is_list:

                    def editor_list_modified ( event ):
                        # Need this to include 'user_object' in closure:
                        user_object
                        if key not in self._no_trait_update:
                            self._no_trait_update[ key ] = None
                            n = event.index
                            try:
                                eval( user_value )[ n:
                                    n + len( event.removed ) ] = event.added
                            except:
                                pass
                            del self._no_trait_update[ key ]

                    self.on_trait_change( editor_list_modified,
                             editor_name + '_items' )
                    self._user_from.append( ( editor_name + '_items',
                                              editor_list_modified ) )

                if mode == 'to':
                    try:
                        setattr( eval( user_ref ), user_name,
                                 getattr( self, editor_name ) )
                    except:
                        pass

    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        pass

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return None

