#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   03/05/2007
#  
#-------------------------------------------------------------------------------

""" Defines classes used to implement and manage various trait listener 
    patterns.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import string
import weakref

from string \
    import whitespace
    
from weakref \
    import WeakKeyDictionary
    
from types \
    import MethodType

from has_traits \
    import HasTraits, HasPrivateTraits
    
from trait_base \
    import Undefined
    
from traits \
    import Property
    
from trait_types \
    import Str, Int, Bool, Instance, List, Enum, Any

from trait_errors \
    import TraitError
    
from trait_notifiers \
   import TraitChangeNotifyWrapper

#---------------------------------------------------------------------------
#  Constants:  
#---------------------------------------------------------------------------

# The name of the dictionary used to store active listeners
TraitsListener = '__traits_listener__'

# End of String marker
EOS = '\0'

# Types of traits that can be listened to

SIMPLE_LISTENER = '_register_simple'
LIST_LISTENER   = '_register_list'
DICT_LISTENER   = '_register_dict'

# Mapping from trait default value types to listener types
type_map = {
    5: LIST_LISTENER,
    6: DICT_LISTENER
}

# Listener types:
ANY_LISTENER = 0
SRC_LISTENER = 1
DST_LISTENER = 2

ListenerType = {
    0: ANY_LISTENER,
    1: DST_LISTENER,
    2: DST_LISTENER,
    3: SRC_LISTENER,
    4: SRC_LISTENER
}

# Invalid destination ( object, name ) reference marker (i.e. ambiguous):
INVALID_DESTINATION = ( None, None )

# Characters valid in a traits name:
name_chars = string.ascii_letters + string.digits + '_'

#-------------------------------------------------------------------------------
#  Metadata filters:
#-------------------------------------------------------------------------------

def is_not_none ( value ): return (value is not None)
def is_none ( value ):     return (value is None)
    
#-------------------------------------------------------------------------------
#  'ListenerBase' class:
#-------------------------------------------------------------------------------

class ListenerBase ( HasPrivateTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The handler to be called when any listened to trait is changed:
    #handler = Any
    
    # The dispatch mechanism to use when invoking the handler:
    #dispatch = Str
    
    # The next level (if any) of ListenerBase object to be called when any of
    # our listened to traits is changed:
    #next = Instance( ListenerBase )
    
    # The type of handler being used:
    #type = Enum( ANY_LISTENER, SRC_LISTENER, DST_LISTENER )
    
    # Should changes to this item generate a notification to the handler?
    # notify = Bool
    
    #---------------------------------------------------------------------------
    #  Registers new listeners:
    #---------------------------------------------------------------------------
    
    def register ( self, new ):
        """ Registers new listeners.
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    #  Unregisters any existing listeners:
    #---------------------------------------------------------------------------
    
    def unregister ( self, old ):
        """ Unregisters any existing listeners.
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    #  Handles a trait change for a simple trait:
    #---------------------------------------------------------------------------
    
    def handle ( self, object, name, old, new ):
        """ Handles a trait change for a simple trait.
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Handles a trait change for a list trait:
    #---------------------------------------------------------------------------
    
    def handle_list ( self, object, name, old, new ):
        """ Handles a trait change for a list trait.
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    #  Handles a trait change for a list traits items:
    #---------------------------------------------------------------------------
    
    def handle_list_items ( self, object, name, old, new ):
        """ Handles a trait change for a list traits items.
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Handles a trait change for a dictionary trait:
    #---------------------------------------------------------------------------
    
    def handle_dict ( self, object, name, old, new ):
        """ Handles a trait change for a dictionary trait.
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Handles a trait change for a dictionary traits items:
    #---------------------------------------------------------------------------
    
    def handle_dict_items ( self, object, name, old, new ):
        """ Handles a trait change for a dictionary traits items.
        """
        raise NotImplementedError
    
#-------------------------------------------------------------------------------
#  'ListenerItem' class:
#-------------------------------------------------------------------------------

class ListenerItem ( ListenerBase ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The name of the trait to listen to:
    name = Str
    
    # The name of any metadata that must be present (or not present):
    metadata_name = Str
    
    # Does the specified metadata need to be defined (True) or not defined 
    # (False)?
    metadata_defined = Bool( True )
    
    # The handler to be called when any listened-to trait is changed:
    handler = Any
    
    # A 'wrapped' version of 'handler':
    wrapped_handler = Any
    
    # The dispatch mechanism to use when invoking the handler:
    dispatch = Str
    
    # The next level (if any) of ListenerBase object to be called when any of
    # this object's listened-to traits is changed:
    next = Instance( ListenerBase )
    
    # The type of handler being used:
    type = Enum( ANY_LISTENER, SRC_LISTENER, DST_LISTENER )
    
    # Should changes to this item generate a notification to the handler?
    notify = Bool( True )
    
    # Is the associated handler a special list handler that handles both
    # 'foo' and 'foo_items' events by receiving a list of 'deleted' and 'added'
    # items as the 'old' and 'new' arguments?
    is_list_handler = Bool( False )
    
    # A dictionary mapping objects to a list of all current active
    # (*name*, *type*) listener pairs, where *type* defines the type of 
    # listener, one of: (SIMPLE_LISTENER, LIST_LISTENER, DICT_LISTENER).
    active = Instance( WeakKeyDictionary, () )
    
    #-- 'ListenerBase' Class Method Implementations ----------------------------            
        
    #---------------------------------------------------------------------------
    #  Registers new listeners:
    #---------------------------------------------------------------------------
    
    def register ( self, new ):
        """ Registers new listeners.
        """
        # Make sure we actually have an object to set listeners on and that it
        # has not already been registered (cycle breaking):
        if (new is None) or (new in self.active):
            return INVALID_DESTINATION
            
        # Create a dictionary of {name: trait_values} that match the object's
        # definition for the 'new' object:
        name = self.name
        last = name[-1:]
        if last == '*':
            # Handle trait matching based on a common name prefix and/or 
            # matching trait metadata:
            metadata = {}
            if self.metadata_name != '':
                if self.metadata_defined:
                    metadata[ self.metadata_name ] = is_not_none
                else:
                    metadata[ self.metadata_name ] = is_none
                    
            # Get all object traits with matching metadata:
            traits = new.traits( **metadata )
            
            # If a name prefix was specified, filter out only the names that
            # start with the specified prefix:
            name = name[:-1]
            if name != '':
                n      = len( name )
                traits = dict( [ ( aname, atrait ) 
                                 for aname, atrait in traits.items()
                                 if name == aname[ : n ] ] )
        else:
            # Determine if the trait is optional or not:
            optional = (last == '?')
            if optional:
                name = name[:-1]
                
            # Else, no wildcard matching, just get the specified trait:
            trait = new.trait( name )
            
            # Try to get the object trait:
            if trait is None:
                # Raise an error if trait is not defined and not optional:
                
                # fixme: Properties which are lists don't implement the
                # '..._items' sub-trait, which can cause a failure here when
                # used with an editor that sets up listeners on the items...
                if not optional:
                    raise TraitError( "'%s' object has no '%s' trait" % (
                                      new.__class__.__name__, name ) )
                                      
                # Otherwise, just skip it:
                traits = {}
            else:
                # Create a result dictionary containing just the single trait:
                traits = { name: trait }
            
        # For each item, determine its type (simple, list, dict):
        self.active[ new ] = active = []
        for name, trait in traits.items():
            
            # Determine whether the trait type is simple, list or dictionary:
            type    = SIMPLE_LISTENER
            handler = trait.handler
            if handler is not None:
                type = type_map.get( handler.default_value_type, 
                                     SIMPLE_LISTENER )
                                     
            # Add the name and type to the list of traits being registered:
            active.append( ( name, type ) )
            
            # Set up the appropriate trait listeners on the object for the
            # current trait:
            value = getattr( self, type )( new, name, False )
               
        if len( traits ) == 1:
            return value
            
        return INVALID_DESTINATION
    
    #---------------------------------------------------------------------------
    #  Unregisters any existing listeners:
    #---------------------------------------------------------------------------
    
    def unregister ( self, old ):
        """ Unregisters any existing listeners.
        """
        if old is not None:
            active = self.active.get( old )
            if active is not None:
                del self.active[ old ]
                for name, type in active:
                    getattr( self, type )( old, name, True )
    
    #---------------------------------------------------------------------------
    #  Handles a trait change for an intermediate link trait:
    #---------------------------------------------------------------------------
    
    def handle_simple ( self, object, name, old, new ):
        """ Handles a trait change for an intermediate link trait.
        """
        self.next.unregister( old )
        self.next.register( new )
    
    def handle_src ( self, object, name, old, new ):
        """ Handles a trait change for an intermediate link trait when the
            notification is for the link change itself.
        """
        self.handle_simple( object, name, old, new )
            
        self.wrapped_handler( object, name, old, new )
    
    def handle_dst ( self, object, name, old, new ):
        """ Handles a trait change for an intermediate link trait when the
            notification is for the final destination trait.
        """
        self.next.unregister( old )
        
        object, name = self.next.register( new )
        if object is None:
            raise TraitError( "on_trait_change handler signature is "
                      "incompatible with a change to an intermediate trait" )
                              
        self.wrapped_handler( object, name, old, 
                              getattr( object, name, Undefined ) )
        
    #---------------------------------------------------------------------------
    #  Handles a trait change for a list trait:
    #---------------------------------------------------------------------------
    
    def handle_list ( self, object, name, old, new ):
        """ Handles a trait change for a list trait.
        """
        unregister = self.next.unregister
        for obj in old:
            unregister( obj )
                
        register = self.next.register
        for obj in new:
            register( obj )
    
    def handle_list_src ( self, object, name, old, new ):
        """ Handles a trait change for a list trait with notification.
        """
        self.handle_list( object, name, old, new )
                
        self.wrapped_handler( object, name, old, new )
    
    #---------------------------------------------------------------------------
    #  Handles a trait change for a list traits items:
    #---------------------------------------------------------------------------
    
    def handle_list_items ( self, object, name, old, new ):
        """ Handles a trait change for items of a list trait.
        """
        unregister = self.next.unregister
        for obj in new.removed:
            unregister( obj )
                
        register = self.next.register
        for obj in new.added:
            register( obj )
     
    def handle_list_items_src ( self, object, name, old, new ):
        """ Handles a trait change for items of a list trait with notification.
        """
        self.handle_list_items( object, name, old, new )
                
        self.wrapped_handler( object, name, old, new )
     
    def handle_list_items_special ( self, object, name, old, new ):
        """ Handles a trait change for items of a list trait with notification.
        """
        self.wrapped_handler( object, name, new.removed, new.added )
        
    #---------------------------------------------------------------------------
    #  Handles a trait change for a dictionary trait:
    #---------------------------------------------------------------------------
    
    def handle_dict ( self, object, name, old, new ):
        """ Handles a trait change for a dictionary trait.
        """
        unregister = self.next.unregister
        for obj in old.values():
            unregister( obj )
                
        register = self.next.register
        for obj in new.values():
            register( obj )
    
    def handle_dict_src ( self, object, name, old, new ):
        """ Handles a trait change for a dictionary trait with notifications.
        """
        self.handle_dict( object, name, old, new )
                
        self.wrapped_handler( object, name, old, new )
        
    #---------------------------------------------------------------------------
    #  Handles a trait change for a dictionary traits items:
    #---------------------------------------------------------------------------
    
    def handle_dict_items ( self, object, name, old, new ):
        """ Handles a trait change for items of a dictionary trait.
        """
        unregister = self.next.unregister
        for obj in new.removed.values():
            unregister( obj )
                
        register = self.next.register
        for obj in new.added.values():
            register( obj )
                
        if len( new.changed ) > 0:
            dict = getattr( object, name )
            for key, obj in new.changed.items():
                unregister( obj )
                register( dict[ key ] )
    
    def handle_dict_items_src ( self, object, name, old, new ):
        """ Handles a trait change for items of a dictionary trait with
            notification.
        """
        self.handle_dict_items( object, name, old, new )
                
        self.wrapped_handler( object, name, old, new )

    #---------------------------------------------------------------------------
    #  Handles an invalid intermediate trait change to a handler that must be
    #  applied to the final destination object.trait: 
    #---------------------------------------------------------------------------
    
    def handle_error ( self ):
        """ Handles an invalid intermediate trait change to a handler that must 
            be applied to the final destination object.trait.
        """
        raise TraitError( "on_trait_change handler signature is "
                  "incompatible with a change to an intermediate trait" )
                
    #-- Event Handlers ---------------------------------------------------------
    
    #---------------------------------------------------------------------------
    #  Handles the 'handler' trait being changed:
    #---------------------------------------------------------------------------
    
    def _handler_changed ( self, handler ):
        """ Handles the **handler** trait being changed.
        """
        if self.next is not None:
            self.next.handler = handler
    
    #---------------------------------------------------------------------------
    #  Handles the 'wrapped_handler' trait being changed:
    #---------------------------------------------------------------------------
    
    def _wrapped_handler_changed ( self, wrapped_handler ):
        """ Handles the 'wrapped_handler' trait being changed.
        """
        if self.next is not None:
            self.next.wrapped_handler = wrapped_handler
    
    #---------------------------------------------------------------------------
    #  Handles the 'dispatch' trait being changed:
    #---------------------------------------------------------------------------
    
    def _dispatch_changed ( self, dispatch ):
        """ Handles the **dispatch** trait being changed.
        """
        if self.next is not None:
            self.next.dispatch = dispatch
        
    #-- Private Methods --------------------------------------------------------
    
    #---------------------------------------------------------------------------
    #  Registers a handler for a simple trait:
    #---------------------------------------------------------------------------
    
    def _register_simple ( self, object, name, remove ):
        """ Registers a handler for a simple trait.
        """
        next = self.next
        if next is None:
            handler = self.handler()
            if handler is not Undefined:
                object._on_trait_change( handler, name, remove = remove,
                                         dispatch = self.dispatch )
            return ( object, name )
        
        if self.notify:
            if self.type == DST_LISTENER:
                handler = self.handle_dst
            else:
                handler = self.handle_src
        else:
            handler = self.handle_simple
        
        object._on_trait_change( handler, name, 
                                 remove = remove, dispatch = self.dispatch )
    
        if remove:
            return next.unregister( getattr( object, name ) )
        
        return next.register( getattr( object, name ) )
        
    #---------------------------------------------------------------------------
    #  Registers a handler for a list trait:  
    #---------------------------------------------------------------------------
                                    
    def _register_list ( self, object, name, remove ):        
        """ Registers a handler for a list trait.
        """
        next = self.next
        if next is None:
            handler = self.handler()
            if handler is not Undefined:
                object._on_trait_change( handler, name, remove = remove, 
                                         dispatch = self.dispatch )
        
                if self.is_list_handler:
                    object._on_trait_change( self.handle_list_items_special,
                                             name + '_items', remove = remove,
                                             dispatch = self.dispatch )
                elif self.type == ANY_LISTENER:
                    object._on_trait_change( handler, name + '_items', 
                                     remove = remove, dispatch = self.dispatch )
                                    
            return ( object, name )
           
        if self.notify:
            if self.type == DST_LISTENER:
                handler = handler_items = self.handle_error
            else:
                handler       = self.handle_list_src
                handler_items = self.handle_list_items_src
        else:
            handler       = self.handle_list
            handler_items = self.handle_list_items

        object._on_trait_change( handler, name, 
                                 remove = remove, dispatch = self.dispatch )
            
        object._on_trait_change( handler_items, name + '_items', 
                                 remove = remove, dispatch = self.dispatch )
                                
        if remove:
            handler = next.unregister
        else:
            handler = next.register
            
        for obj in getattr( object, name ):
            handler( obj )
            
        return INVALID_DESTINATION
        
    #---------------------------------------------------------------------------
    #  Registers a handler for a dictionary trait:
    #---------------------------------------------------------------------------
                                    
    def _register_dict ( self, object, name, remove ):        
        """ Registers a handler for a dictionary trait.
        """
        next = self.next
        if next is None:
            handler = self.handler()
            if handler is not Undefined:
                object._on_trait_change( handler, name, remove = remove, 
                                         dispatch = self.dispatch )
                                
                if self.type == ANY_LISTENER:
                    object._on_trait_change( handler, name + '_items', 
                                     remove = remove, dispatch = self.dispatch )
                                    
            return ( object, name )
           
        if self.notify:
            if self.type == DST_LISTENER:
                handler = handler_items = self.handle_error
            else:
                handler       = self.handle_dict_src
                handler_items = self.handle_dict_items_src
        else:
            handler       = self.handle_dict
            handler_items = self.handle_dict_items

        object._on_trait_change( handler, name, 
                                 remove = remove, dispatch = self.dispatch )
            
        object._on_trait_change( handler_items, name + '_items', 
                                 remove = remove, dispatch = self.dispatch )
                                
        if remove:
            handler = next.unregister
        else:
            handler = next.register
            
        for obj in getattr( object, name ).values():
            handler( obj )
            
        return INVALID_DESTINATION

#-------------------------------------------------------------------------------
#  'ListenerGroup' class:
#-------------------------------------------------------------------------------

class ListenerGroup ( ListenerBase ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The handler to be called when any listened-to trait is changed
    handler = Property
    
    # A 'wrapped' version of 'handler':
    wrapped_handler = Property
    
    # The dispatch mechanism to use when invoking the handler:
    dispatch = Property
    
    # The next level (if any) of ListenerBase object to be called when any of
    # this object's listened-to traits is changed
    next = Property
    
    # The type of handler being used:
    type = Property
    
    # Should changes to this item generate a notification to the handler?
    notify = Property

    # The list of ListenerBase objects in the group
    items = List( ListenerBase )
    
    #-- Property Implementations -----------------------------------------------
    
    def _set_handler ( self, handler ):
        if self._handler is None:
            self._handler = handler
            for item in self.items:
                item.handler = handler
    
    def _set_wrapped_handler ( self, wrapped_handler ):
        if self._wrapped_handler is None:
            self._wrapped_handler = wrapped_handler
            for item in self.items:
                item.wrapped_handler = wrapped_handler
    
    def _set_dispatch ( self, dispatch ):
        if self._dispatch is None:
            self._dispatch = dispatch
            for item in self.items:
                item.dispatch = dispatch
            
    def _set_next ( self, next ):
        for item in self.items:
            item.next = next
            
    def _set_type ( self, type ):
        for item in self.items:
            item.type = type
            
    def _set_notify ( self, notify ):
        for item in self.items:
            item.notify = notify
            
    #-- 'ListenerBase' Class Method Implementations ----------------------------            
   
    #---------------------------------------------------------------------------
    #  Registers new listeners:
    #---------------------------------------------------------------------------
    
    def register ( self, new ):
        """ Registers new listeners.
        """
        for item in self.items:
            item.register( new )
            
        return INVALID_DESTINATION
    
    #---------------------------------------------------------------------------
    #  Unregisters any existing listeners:
    #---------------------------------------------------------------------------
    
    def unregister ( self, old ):
        """ Unregisters any existing listeners.
        """
        for item in self.items:
            item.unregister( old )
              
#-------------------------------------------------------------------------------
#  'ListenerParser' class:  
#-------------------------------------------------------------------------------
                        
class ListenerParser ( HasPrivateTraits ):
    
    #-------------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------------
    
    # The string being parsed
    text = Str
    
    # The current parse index within the string
    index = Int
    
    # The next character from the string being parsed
    next = Property
    
    # The next non-whitespace character
    skip_ws = Property
    
    # Backspaces to the last character processed
    backspace = Property 
    
    # The ListenerBase object resulting from parsing **text**
    listener = Instance( ListenerBase )
    
    #-- Property Implementations -----------------------------------------------
    
    def _get_next ( self ):
        try:
            result = self.text[ self.index ]
            self.index += 1
            return result
        except:
            self.index += 1
            return EOS
            
    def _get_backspace ( self ):
        self.index = max( 0, self.index - 1 )
    
    def _get_skip_ws ( self ):
        while True:
            c = self.next
            if c not in whitespace:
                return c
        
    #-- object Method Overrides ------------------------------------------------
    
    def __init__ ( self, text = '', **traits ):
        self.text = text
        super( ListenerParser, self ).__init__( **traits )
        
    #-- Private Methods --------------------------------------------------------
    
    #---------------------------------------------------------------------------
    #  Parses the text and returns the appropriate collection of ListenerBase
    #  objects described by the text:
    #---------------------------------------------------------------------------
    
    def parse ( self ):
        """ Parses the text and returns the appropriate collection of 
            ListenerBase objects described by the text.
        """
        return self.parse_group( EOS )
    
    #---------------------------------------------------------------------------
    #  Parses the contents of a group:
    #---------------------------------------------------------------------------
    
    def parse_group ( self, terminator = ']' ):
        """ Parses the contents of a group.
        """
        items = []
        while True:
            items.append( self.parse_item( terminator ) )
            
            c = self.skip_ws
            if c is terminator:
                break
                
            if c != ',':
                if terminator == EOS:
                    self.error( "Expected ',' or end of string" )
                else:
                    self.error( "Expected ',' or '%s'" % terminator )
            
        if len( items ) == 1:
            return items[0]
            
        return ListenerGroup( items = items )
        
    #---------------------------------------------------------------------------
    #  Parses a single, complete listener item/group string:
    #---------------------------------------------------------------------------
             
    def parse_item ( self, terminator ):
        """ Parses a single, complete listener item or group string.
        """
        c = self.skip_ws
        if c == '[':
            result = self.parse_group()
            c      = self.skip_ws
        else:
            name = ''
            if c in name_chars:
                while True:
                    name += c
                    c = self.next
                    if c not in name_chars:
                        break
                if c == ' ':
                    c = self.skip_ws
                    
            result = ListenerItem( name = name )
            
            if c in '+-':
                result.name += '*'
                result.metadata_defined = (c == '+')
                self.parse_metadata( result )
                c = self.skip_ws
            elif c == '?':
                if len( name ) == 0:
                    self.error( "Expected non-empty name preceding '?'" )
                result.name += '?'
                c = self.skip_ws
        
        cycle = (c == '*')
        if cycle:
            c = self.skip_ws
            
        if c in '.:':
            result.notify = (c == '.')
            next = self.parse_item( terminator )
            if cycle:
                result.next = lg = ListenerGroup( items = [ next, result ] )
                result      = lg
            else:
                result.next = next
                
            return result
            
        if c == '[':
            if (self.skip_ws == ']') and (self.skip_ws == terminator):
                self.backspace
                result.is_list_handler = True
            else:
                self.error( "Expected '[]' at the end of an item" )
        else:
            self.backspace
            
        if cycle:
            result.next = result
                
        return result
        
    #---------------------------------------------------------------------------
    #  Parses the metadata portion of a listener item:
    #---------------------------------------------------------------------------
    
    def parse_metadata ( self, item ):
        """ Parses the metadata portion of a listener item.
        """
        name = ''
        c    = self.skip_ws
        while c in name_chars:
            name += c
            c     = self.next
                
        item.metadata_name = name
        self.backspace
                                    
    #---------------------------------------------------------------------------
    #  Raises a syntax error:
    #---------------------------------------------------------------------------
    
    def error ( self, msg ):
        """ Raises a syntax error.
        """
        raise TraitError( "%s at column %d of '%s'" %
                          ( msg, self.index, self.text ) ) 
                          
    #-- Event Handlers ---------------------------------------------------------
    
    #---------------------------------------------------------------------------
    #  Handles the 'text' trait being changed:
    #---------------------------------------------------------------------------
    
    def _text_changed ( self ):
        self.index    = 0
        self.listener = self.parse()

#-------------------------------------------------------------------------------
#  'ListenerNotifyWrapper' class:
#-------------------------------------------------------------------------------

class ListenerNotifyWrapper ( TraitChangeNotifyWrapper ):
    
    #-- TraitChangeNotifyWrapper Method Overrides ------------------------------
    
    def __init__ ( self, handler, owner, id, listener ):
        self.type     = ListenerType.get( self.init( handler, owner ) )
        self.id       = id
        self.listener = listener
    
    def listener_deleted ( self, ref ):
        owner = self.owner
        dict  = owner.__dict__.get( TraitsListener )
        listeners = dict.get( self.id )
        listeners.remove( self )
        if len( listeners ) == 0:
            del dict[ self.id ]
            if len( dict ) == 0:
                del owner.__dict__[ TraitsListener ]
            # fixme: Is the following line necessary, since all registered
            # notifiers should be getting the same 'listener_deleted' call:
            self.listener.unregister( owner )
            
        self.object = self.owner = self.listener = None
                    
#-------------------------------------------------------------------------------
#  'ListenerHandler' class:  
#-------------------------------------------------------------------------------

class ListenerHandler:

    def __init__ ( self, handler ):
        if type( handler ) is MethodType:
            object = handler.im_self
            if object is not None:
                self.object = weakref.ref( object, self.listener_deleted )
                self.name   = handler.__name__
                
                return
                
        self.handler = handler
        
    def __call__ ( self ):
        result = getattr( self, 'handler', None )
        if result is not None:
            return result
            
        return getattr( self.object(), self.name )

    def listener_deleted ( self, ref ):
        self.handler = Undefined

