#-------------------------------------------------------------------------------
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
#  Date:   05/20/2005
#
#-------------------------------------------------------------------------------

""" Defines KeyBinding and KeyBindings classes, which manage the mapping of
    keystroke events into method calls on controller objects that are supplied
    by the application.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import (Any, Event, HasPrivateTraits, HasStrictTraits, Instance, List,
    Property, Str, cached_property, on_trait_change)

from .api import HGroup, Item, KeyBindingEditor, ListEditor, View, toolkit

from ..trait_base import SequenceTypes

#-------------------------------------------------------------------------------
#  Key binding trait definition:
#-------------------------------------------------------------------------------

# Trait definition for key bindings
Binding = Str( event = 'binding', editor = KeyBindingEditor() )

#-------------------------------------------------------------------------------
#  'KeyBinding' class:
#-------------------------------------------------------------------------------

class KeyBinding ( HasStrictTraits ):
    """ Binds one or two keystrokes to a method.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # First key binding
    binding1 = Binding

    # Second key binding
    binding2 = Binding

    # Description of what application function the method performs
    description = Str

    # Name of controller method the key is bound to
    method_name = Str

    # KeyBindings object that "owns" the KeyBinding
    owner = Instance( 'KeyBindings' )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View(
        HGroup(
            Item( 'binding1' ),
            Item( 'binding2' ),
            Item( 'description', style = 'readonly' ),
            show_labels = False
        )
    )

    #---------------------------------------------------------------------------
    #  Handles a binding trait being changed:
    #---------------------------------------------------------------------------

    def _binding_changed ( self ):
        if self.owner is not None:
            self.owner.binding_modified = self

#-------------------------------------------------------------------------------
#  'KeyBindings' class:
#-------------------------------------------------------------------------------

class KeyBindings ( HasPrivateTraits ):
    """ A set of key bindings.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Set of defined key bindings (redefined dynamically)
    bindings = List( KeyBinding )

    # Optional prefix to add to each method name
    prefix = Str

    # Optional suffix to add to each method name
    suffix = Str

    #-- Private Traits ---------------------------------------------------------

    # The (optional) list of controllers associated with this KeyBindings
    # object. The controllers may also be provided with the 'do' method:
    controllers = List( transient = True )

    # The 'parent' KeyBindings object of this one (if any):
    parent = Instance( 'KeyBindings', transient = True )

    # The root of the KeyBindings tree this object is part of:
    root = Property( depends_on = 'parent' )

    # The child KeyBindings of this object (if any):
    children = List( transient = True )

    # Event fired when one of the contained KeyBinding objects is changed
    binding_modified = Event( KeyBinding )

    # Control that currently has the focus (if any)
    focus_owner = Any( transient = True )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( [ Item( 'bindings',
                                style      = 'custom',
                                show_label = False,
                                editor     = ListEditor( style = 'custom' ) ),
                          '|{Click on an entry field, then press the key to '
                          'assign. Double-click a field to clear it.}<>' ],
                        title     = 'Update Key Bindings',
                        kind      = 'livemodal',
                        resizable = True,
                        width     = 0.4,
                        height    = 0.4 )

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *bindings, **traits ):
        super( KeyBindings, self ).__init__( **traits )

        if (len( bindings ) == 1) and isinstance( bindings[0], SequenceTypes ):
            bindings = bindings[0]

        n = len( bindings )
        self.add_trait( 'bindings', List( KeyBinding, minlen = n,
                                                      maxlen = n,
                                                      mode   = 'list' ) )
        self.bindings = [ binding.set( owner = self ) for binding in bindings ]

    #---------------------------------------------------------------------------
    #  Processes a keyboard event:
    #---------------------------------------------------------------------------

    def do ( self, event, controllers = [], *args, **kw ):
        """ Processes a keyboard event.
        """
        if isinstance( controllers, dict ):
            controllers = controllers.values()
        elif not isinstance( controllers, SequenceTypes ):
            controllers = [ controllers ]
        else:
            controllers = list( controllers )

        return self._do( toolkit().key_event_to_name( event ),
                         controllers, args, kw.get( 'recursive', False ) )

    #---------------------------------------------------------------------------
    #  Merges another set of key bindings into this set:
    #---------------------------------------------------------------------------

    def merge ( self, key_bindings ):
        """ Merges another set of key bindings into this set.
        """
        binding_dic = {}
        for binding in self.bindings:
            binding_dic[ binding.method_name ] = binding

        for binding in key_bindings.bindings:
            binding2 = binding_dic.get( binding.method_name )
            if binding2 is not None:
                binding2.binding1 = binding.binding1
                binding2.binding2 = binding.binding2

    #---------------------------------------------------------------------------
    #  Returns a clone of the KeyBindings object:
    #---------------------------------------------------------------------------

    def clone ( self, **traits ):
        """ Returns a clone of the KeyBindings object.
        """
        return self.__class__( *self.bindings, **traits ).set(
                               **self.get( 'prefix', 'suffix' ) )

    #---------------------------------------------------------------------------
    #  Dispose of the object:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Dispose of the object.
        """
        if self.parent is not None:
            self.parent.children.remove( self )

        del self.controllers
        del self.children
        del self.bindings

        self.parent = self._root = self.focus_owner = None

    #---------------------------------------------------------------------------
    #  Edits a possibly hierarchical set of KeyBindings:
    #---------------------------------------------------------------------------

    def edit ( self ):
        """ Edits a possibly hierarchical set of KeyBindings.
        """
        bindings = list( set( self.root._get_bindings( [] ) ) )
        bindings.sort( lambda l, r:
            cmp( '%s%02d' % ( l.binding1[-1:], len( l.binding1 ) ),
                 '%s%02d' % ( r.binding1[-1:], len( r.binding1 ) ) ) )
        KeyBindings( bindings ).edit_traits()

    #---------------------------------------------------------------------------
    #  Returns the current binding for a specified key (if any):
    #---------------------------------------------------------------------------

    def key_binding_for ( self, binding, key_name ):
        """ Returns the current binding for a specified key (if any).
        """
        if key_name != '':
            for a_binding in self.bindings:
                if ((a_binding is not binding) and
                    ((key_name == a_binding.binding1) or
                     (key_name == a_binding.binding2))):
                    return a_binding

        return None

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_root ( self ):
        root = self
        while root.parent is not None:
            root = root.parent

        return root

    #-- Event Handlers ---------------------------------------------------------

    def _binding_modified_changed ( self, binding ):
        """ Handles a binding being changed.
        """
        binding1 = binding.binding1
        binding2 = binding.binding2
        for a_binding in self.bindings:
            if binding is not a_binding:
                if binding1 == a_binding.binding1:
                    a_binding.binding1 = ''
                if binding1 == a_binding.binding2:
                    a_binding.binding2 = ''
                if binding2 == a_binding.binding1:
                    a_binding.binding1 = ''
                if binding2 == a_binding.binding2:
                    a_binding.binding2 = ''

    def _focus_owner_changed ( self, old, new ):
        """ Handles the focus owner being changed.
        """
        if old is not None:
            old.border_size = 0

    @on_trait_change( 'children[]' )
    def _children_modified ( self, removed, added ):
        """ Handles child KeyBindings being added to the object.
        """
        for item in added:
            item.parent = self

    #-- object Method Overrides ------------------------------------------------

    #---------------------------------------------------------------------------
    #  Restores the state of a previously pickled object:
    #---------------------------------------------------------------------------

    def __setstate__ ( self, state ):
        """ Restores the state of a previously pickled object.
        """
        n = len( state[ 'bindings' ] )
        self.add_trait( 'bindings', List( KeyBinding, minlen = n, maxlen = n ) )
        self.__dict__.update( state )
        self.bindings = self.bindings[:]

    #-- Private Methods --------------------------------------------------------

    def _get_bindings ( self, bindings ):
        """ Returns all of the bindings of this object and all of its children.
        """
        bindings.extend( self.bindings )
        for child in self.children:
            child._get_bindings( bindings )

        return bindings

    def _do ( self, key_name, controllers, args, recursive ):
        """ Process the specified key for the specified set of controllers for
            this KeyBindings object and all of its children.
        """
        # Search through our own bindings for a match:
        for binding in self.bindings:
            if (key_name == binding.binding1) or (key_name == binding.binding2):
                method_name = '%s%s%s' % (
                              self.prefix, binding.method_name, self.suffix )
                for controller in (controllers + self.controllers):
                    method = getattr( controller, method_name, None )
                    if method is not None:
                        result = method( *args )
                        if result is not False:
                            return True

                if binding.method_name == 'edit_bindings':
                    self.edit()
                    return True

        # If recursive, continue searching through a children's bindings:
        if recursive:
            for child in self.children:
                if child._do( key_name, controllers, args, recursive ):
                    return True

        # Indicate no one processed the key:
        return False

