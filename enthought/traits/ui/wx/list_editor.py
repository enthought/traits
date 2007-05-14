#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#  
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the various list editors and the list editor factory for the 
wxPython user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

import wx.lib.scrolledpanel as wxsp

from constants \
    import scrollbar_dx
    
from editor_factory \
    import EditorFactory
    
from editor \
    import Editor
    
from enthought.traits.api \
    import Trait, HasTraits, BaseTraitHandler, Range, Str, Any, Instance, \
           Property, false
    
from enthought.traits.trait_base \
    import user_name_for, enumerate
    
from enthought.traits.ui.api \
    import View, Item, EditorFactory
    
from enthought.traits.ui.ui_traits \
    import style_trait, AView
    
from enthought.traits.ui.dockable_view_element \
    import DockableViewElement
    
from enthought.pyface.dock.core \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl, \
           DockStyle
    
from helper \
    import bitmap_cache
    
from menu \
    import MakeMenu
    
from image_control \
    import ImageControl

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Trait whose value is a BaseTraitHandler object
handler_trait = Instance( BaseTraitHandler )

# The visible number of rows displayed
rows_trait = Range( 1, 50, 5,
                    desc = 'the number of list rows to display' )
                    
editor_trait = Instance( EditorFactory )                    

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for list editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The editor to use for each list item:
    editor = editor_trait
    
    # The style of editor to use for each item:
    style = style_trait
    
    # The trait handler for each list item:
    trait_handler = handler_trait 
    
    # Number of list rows to display:
    rows = rows_trait 

    # Use a notebook for a custom view?
    use_notebook = false
    
    #-- Notebook Specific Traits -----------------------------------------------
    
    # Are notebook items deletable?
    deletable = false   
    
    # Dock page style to use for each DockControl:
    dock_style = DockStyle 
    
    # Export class for each item in a notebook:
    export = Str 
    
    # Name of the view to use in notebook mode:
    view = AView
    
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
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             kind        = self.style + '_editor' )
    
    def custom_editor ( self, ui, object, name, description, parent ):
        if self.use_notebook:
            return NotebookEditor( parent,
                                   factory     = self, 
                                   ui          = ui, 
                                   object      = object, 
                                   name        = name, 
                                   description = description )
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             kind        = self.style + '_editor' )
    
    def text_editor ( self, ui, object, name, description, parent ):
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             kind        = 'text_editor' )
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description,
                             kind        = 'readonly_editor' )
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of editor for lists, which displays a scrolling list box
    with only one item visible at a time. A icon next to the list box displays
    a menu of operations on the list.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # The kind of editor to create for each list item
    kind = Str  
    
    #---------------------------------------------------------------------------
    #  Class constants:  
    #---------------------------------------------------------------------------
    
    # Whether the list is displayed in a single row
    single_row = True
    
    #---------------------------------------------------------------------------
    #  Normal list item menu:
    #---------------------------------------------------------------------------
    
    # Menu for modifying the list
    list_menu = """
       Add Before     [_menu_before]: self.add_before()
       Add After      [_menu_after]:  self.add_after()
       ---
       Delete         [_menu_delete]: self.delete_item()
       ---
       Move Up        [_menu_up]:     self.move_up()
       Move Down      [_menu_down]:   self.move_down()
       Move to Top    [_menu_top]:    self.move_top() 
       Move to Bottom [_menu_bottom]: self.move_bottom()
    """
 
    #---------------------------------------------------------------------------
    #  Empty list item menu:
    #---------------------------------------------------------------------------
    
    empty_list_menu = """
       Add: self.add_empty()
    """
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Initialize the trait handler to use:
        trait_handler = self.factory.trait_handler
        if trait_handler is None:
            trait_handler = self.object.base_trait( self.name ).handler
        self._trait_handler = trait_handler
        
        # Create a scrolled window to hold all of the list item controls:
        self.control = wxsp.ScrolledPanel( parent, -1 )
        self.control.SetAutoLayout( True )
        
        # Remember the editor to use for each individual list item:
        editor = self.factory.editor 
        if editor is None:
            editor = trait_handler.item_trait.get_editor() 
        self._editor = getattr( editor, self.kind )
                     
        # Set up the additional 'list items changed' event handler needed for
        # a list based trait:
        self.context_object.on_trait_change( self.update_editor_item, 
                               self.extended_name + '_items?', dispatch = 'ui' )
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change( self.update_editor_item, 
                                 self.extended_name + '_items?', remove = True )
        super( SimpleEditor, self ).dispose()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        list_pane = self.control
        editor    = self._editor

        # Disconnect the editor from any control about to be destroyed:        
        for control in list_pane.GetChildren():
            if hasattr( control, '_editor' ):
                control._editor.dispose()
                control._editor.control = None
                
        # Get rid of any previous contents:
        list_pane.SetSizer( None )
        list_pane.DestroyChildren()
        
        # Create all of the list item trait editors:
        trait_handler = self._trait_handler
        resizable     = ((trait_handler.minlen != trait_handler.maxlen) and
                         (self.kind != 'readonly_editor'))
        item_trait    = trait_handler.item_trait
        list_sizer    = wx.FlexGridSizer( 0, 1 + resizable, 0, 0 )
        list_sizer.AddGrowableCol( resizable )
        values        = self.value
        index         = 0
        width, height = 100, 18
        
        is_fake       = (resizable and (len( values ) == 0))
        if is_fake:
            values = [ item_trait.default_value()[1] ]
            
        width = 0
        for value in values:
            width1 = height = 0
            if resizable:       
                control = ImageControl( list_pane,
                                        bitmap_cache( 'list_editor', False ),
                                        -1, self.popup_menu )                                   
                width1, height = control.GetSize()
                width1 += 4
                
            try:
                proxy = ListItemProxy( self.object, self.name, index,
                                       item_trait, value )
                if resizable:
                    control.proxy = proxy
                peditor = editor( self.ui, proxy, 'value', self.description, 
                                  list_pane ).set( object_name = '' )
                peditor.prepare( list_pane )
                pcontrol = peditor.control
                pcontrol.proxy = proxy
            except:
                if not is_fake:
                    raise
                pcontrol = wx.Button( list_pane, -1, 'sample' )
                
            pcontrol.Fit() 
            width2, height2 = size = pcontrol.GetSize()
            pcontrol.SetMinSize( size )
            width  = max( width, width1 + width2 )
            height = max( height, height2 )
            
            if resizable:
                list_sizer.Add( control, 0, wx.LEFT | wx.RIGHT, 2 )
                
            list_sizer.Add( pcontrol, 0, wx.EXPAND )
            index += 1
            
        list_pane.SetSizer( list_sizer )
        
        if is_fake:
           self._cur_control = control   
           self.empty_list()
           control.Destroy()
           pcontrol.Destroy()
           
        rows = 1
        if not self.single_row:
            rows = self.factory.rows
            
        list_pane.SetSize( wx.Size( 
             width + ((trait_handler.maxlen > rows) * scrollbar_dx), 
             height * rows ) )
        list_pane.SetupScrolling()
        list_pane.GetParent().Layout()

    #---------------------------------------------------------------------------
    #  Updates the editor when an item in the object trait changes external to 
    #  the editor:
    #---------------------------------------------------------------------------
        
    def update_editor_item ( self, event ):
        """ Updates the editor when an item in the object trait changes 
        externally to the editor.
        """
        # If this is not a simple, single item update, rebuild entire editor:
        if (len( event.removed ) != 1) or (len( event.added ) != 1):
            self.update_editor()
            return
        
        # Otherwise, find the proxy for this index and update it with the 
        # changed value: 
        for control in self.control.GetChildren():
            proxy = control.proxy
            if proxy.index == event.index:
                proxy.value = event.added[0]
                break

    #---------------------------------------------------------------------------
    #  Creates an empty list entry (so the user can add a new item):
    #---------------------------------------------------------------------------
           
    def empty_list ( self ):
        """ Creates an empty list entry (so the user can add a new item).
        """
        control = ImageControl( self.control,
                                bitmap_cache( 'list_editor', False ),
                                -1, self.popup_empty_menu )                                   
        control.is_empty = True
        proxy    = ListItemProxy( self.object, self.name, -1, None, None )
        pcontrol = wx.StaticText( self.control, -1, '   (Empty List)' )
        pcontrol.proxy = control.proxy = proxy
        self.reload_sizer( [ ( control, pcontrol ) ] )
  
    #---------------------------------------------------------------------------
    #  Reloads the layout from the specified list of ( button, proxy ) pairs:
    #---------------------------------------------------------------------------
          
    def reload_sizer ( self, controls, extra = 0 ):
        """ Reloads the layout from the specified list of ( button, proxy ) 
            pairs.
        """
        sizer = self.control.GetSizer()
        for i in xrange( 2 * len( controls ) + extra ):
            sizer.Remove( 0 )
        index = 0
        for control, pcontrol in controls:
            sizer.Add( control,  0, wx.LEFT | wx.RIGHT, 2 )
            sizer.Add( pcontrol, 1, wx.EXPAND )
            control.proxy.index = index
            index += 1
        sizer.Layout()
        self.control.SetVirtualSize( sizer.GetMinSize() )
       
    #---------------------------------------------------------------------------
    #  Returns the associated object list and current item index:
    #---------------------------------------------------------------------------
     
    def get_info ( self ):
        """ Returns the associated object list and current item index.
        """
        proxy = self._cur_control.proxy
        return ( proxy.list, proxy.index )
        
    #---------------------------------------------------------------------------
    #  Displays the empty list editor popup menu:
    #---------------------------------------------------------------------------
    
    def popup_empty_menu ( self, control ):
        """ Displays the empty list editor popup menu.
        """
        self._cur_control = control
        control.PopupMenuXY( MakeMenu( self.empty_list_menu, self, True, 
                                       control ).menu, 0, 0 )
       
    #---------------------------------------------------------------------------
    #  Displays the list editor popup menu:
    #---------------------------------------------------------------------------
    
    def popup_menu ( self, control ):
        """ Displays the list editor popup menu.
        """
        self._cur_control = control
        # Makes sure that any text that was entered get's added (Pressure #145):
        control.SetFocus() 
        proxy    = control.proxy
        index    = proxy.index
        menu     = MakeMenu( self.list_menu, self, True, control ).menu
        len_list = len( proxy.list )
        not_full = (len_list < self._trait_handler.maxlen)
        self._menu_before.enabled( not_full )
        self._menu_after.enabled(  not_full )
        self._menu_delete.enabled( len_list > self._trait_handler.minlen )
        self._menu_up.enabled(  index > 0 )
        self._menu_top.enabled( index > 0 )
        self._menu_down.enabled(   index < (len_list - 1) )
        self._menu_bottom.enabled( index < (len_list - 1) )
        control.PopupMenuXY( menu, 0, 0 )

    #---------------------------------------------------------------------------
    #  Adds a new value at the specified list index:
    #---------------------------------------------------------------------------
           
    def add_item ( self, offset ):
        """ Adds a new value at the specified list index.
        """
        list, index = self.get_info()
        index      += offset 
        item_trait  = self._trait_handler.item_trait
        dv          = item_trait.default_value()
        if dv[0] == 7:
            func, args, kw = dv[1]
            if kw is None:
                kw = {}
            value = func( *args, **kw )
        else:
            value = dv[1]
        self.value = list[:index] + [ value ] + list[index:]
        self.update_editor()
        
    #---------------------------------------------------------------------------
    #  Inserts a new item before the current item:
    #---------------------------------------------------------------------------
           
    def add_before ( self ):
        """ Inserts a new item before the current item.
        """
        self.add_item( 0 )
        
    #---------------------------------------------------------------------------
    #  Inserts a new item after the current item:
    #---------------------------------------------------------------------------
    
    def add_after ( self ):
        """ Inserts a new item after the current item.
        """
        self.add_item( 1 )
        
    #---------------------------------------------------------------------------
    #  Adds a new item when the list is empty:
    #---------------------------------------------------------------------------
    
    def add_empty ( self ):
        """ Adds a new item when the list is empty.
        """
        list, index = self.get_info()
        self.add_item( 0 )
        
    #---------------------------------------------------------------------------
    #  Delete the current item:
    #---------------------------------------------------------------------------
    
    def delete_item ( self ):
        """ Delete the current item.
        """
        list, index = self.get_info()
        self.value  = list[:index] + list[index+1:]
        self.update_editor()
        
    #---------------------------------------------------------------------------
    #  Move the current item up one in the list:
    #---------------------------------------------------------------------------
       
    def move_up ( self ):
        """ Move the current item up one in the list.
        """
        list, index = self.get_info()
        self.value  = (list[:index-1] + [ list[index], list[index-1] ] + 
                       list[index+1:])
       
    #---------------------------------------------------------------------------
    #  Moves the current item down one in the list:
    #---------------------------------------------------------------------------
    
    def move_down ( self ):
        """ Moves the current item down one in the list.
        """
        list, index = self.get_info()
        self.value  = (list[:index] + [ list[index+1], list[index] ] + 
                       list[index+2:])
        
    #---------------------------------------------------------------------------
    #  Moves the current item to the top of the list:
    #---------------------------------------------------------------------------
    
    def move_top ( self ):
        """ Moves the current item to the top of the list.
        """
        list, index = self.get_info()
        self.value  = [ list[index] ] + list[:index] + list[index+1:]
         
    #---------------------------------------------------------------------------
    #  Moves the current item to the bottom of the list:
    #---------------------------------------------------------------------------
    
    def move_bottom ( self ):
        """ Moves the current item to the bottom of the list.
        """
        list, index = self.get_info()
        self.value  = list[:index] + list[index+1:] + [ list[index] ] 
                                      
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( SimpleEditor ):
    """ Custom style of editor for lists, which displays the items as a series
    of text fields. If the list is editable, an icon next to each item displays
    a menu of operations on the list.
    """
    
    #---------------------------------------------------------------------------
    #  Class constants:  
    #---------------------------------------------------------------------------
    
    # Whether the list is displayed in a single row. This value overrides the 
    # default.
    single_row = False

    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the list editor is scrollable? This values overrides the default.
    scrollable = True 
   
#-------------------------------------------------------------------------------
#  'ListItemProxy' class:
#-------------------------------------------------------------------------------
       
class ListItemProxy ( HasTraits ):
    
    list = Property

    def __init__ ( self, object, name, index, trait, value ):
        super( ListItemProxy, self ).__init__()
        
        self.inited = False
        self.object = object
        self.name   = name
        self.index  = index
        
        if trait is not None:
            self.add_trait( 'value', trait )
            self.value = value
            
        self.inited = (self.index < len( self.list ))
        
    def _get_list ( self ):
        return getattr( self.object, self.name )
        
    def _value_changed ( self, old_value, new_value ):
        if self.inited:
            self.list[ self.index ] = new_value

#-------------------------------------------------------------------------------
#  'NotebookEditor' class:
#-------------------------------------------------------------------------------

class NotebookEditor ( Editor ):
    """ An editor for lists that displays the list as a "notebook" of tabbed
    pages.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # Is the notebook editor scrollable? This values overrides the default:
    scrollable = True
    
    # The currently selected notebook page object:
    selected = Any

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create a DockWindow to hold each separate object's view:
        self.control = DockWindow( parent ).control
        self.control.SetSizer( DockSizer( DockSection() ) )

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait:
        self.context_object.on_trait_change( self.update_editor_item, 
                               self.extended_name + '_items?', dispatch = 'ui' )
                                     
        # Set of selection synchronization:
        self.sync_value( self.factory.selected, 'selected' )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        # Destroy the views on each current notebook page:
        self.close_all()

        # Create a DockControl for each object in the trait's value:
        uis           = self._uis
        dock_controls = []
        for object in self.value:
            dock_control, monitoring = self._create_page( object )
                                     
            # Remember the DockControl for later deletion processing:
            uis.append( [ dock_control, object, monitoring ] )

            dock_controls.append( dock_control )

        # Add the new items to the DockWindow:
        self.add_controls( dock_controls )
        if self.ui.info.initialized:
            self.update_layout()

    #---------------------------------------------------------------------------
    #  Handles some subset of the trait's list being updated:
    #---------------------------------------------------------------------------

    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the trait's list.
        """
        index = event.index

        # Delete the page corresponding to each removed item:
        layout = ((len( event.removed ) + len( event.added )) <= 1)
        for i in range( len( event.removed ) ):
            dock_control, object, monitoring = self._uis[ index ]
            if monitoring:
                object.on_trait_change( self.update_page_name, 
                                     self.factory.page_name[1:], remove = True )
            dock_control.close( layout = layout, force = True )                                        
            del self._uis[ index ]

        # Add a page for each added object:
        dock_controls = []
        first_control = None
        for object in event.added:
            dock_control, monitoring  = self._create_page( object )
            self._uis[ index: index ] = [ [ dock_control, object, monitoring ] ]
            dock_controls.append( dock_control )
            index += 1
            if first_control is None:
                first_control = dock_control

        # Add the new items to the DockWindow:
        self.add_controls( dock_controls )
        if first_control is not None:
            first_control.activate( layout = False )
        self.update_layout()
        
    #---------------------------------------------------------------------------
    #  Closes all currently open notebook pages:  
    #---------------------------------------------------------------------------

    def close_all ( self ):
        """ Closes all currently open notebook pages.
        """
        page_name = self.factory.page_name[1:]
        if self._uis is not None:
            for dock_control, object, monitoring in self._uis:
                if monitoring:
                    object.on_trait_change( self.update_page_name, 
                                                     page_name, remove = True )
                dock_control.close( layout = False, force = True )

        # Reset the list of ui's and dictionary of page name counts:
        self._uis   = []
        self._pages = {}
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change( self.update_editor_item, 
                                self.name + '_items?', remove = True )
        self.close_all()
        super( NotebookEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Adds a group of new DockControls to the view:
    #---------------------------------------------------------------------------

    def add_controls ( self, controls ):
        """ Adds a group of new DockControls to the view.
        """
        if len( controls ) > 0: 
            section = self.control.GetSizer().GetContents()
            if ((len( section.contents ) == 0) or 
                (not isinstance( section.contents[-1], DockRegion ))):
                section.contents.append( DockRegion( contents = controls ) )
            else:
                section.contents[-1].contents.extend( controls )

    #---------------------------------------------------------------------------
    #  Updates the layout of the DockWindow:
    #---------------------------------------------------------------------------

    def update_layout ( self ):
        """ Updates the layout of the DockWindow.
        """
        self.control.Layout()
        self.control.Refresh()

    #---------------------------------------------------------------------------
    #  Handles the trait defining a particular page's name being changed:
    #---------------------------------------------------------------------------

    def update_page_name ( self, object, name, old, new ):
        """ Handles the trait defining a particular page's name being changed.
        """
        for i, value in enumerate( self._uis ):
            dock_control, ui_object, monitoring = value
            if object is ui_object:
                if dock_control.control is not None:
                    name    = None
                    handler = getattr( self.ui.handler, '%s_%s_page_name' % 
                                       ( self.object_name, self.name ), None )
                    if handler is not None:
                        name = handler( self.ui.info, object )
                    if name is None:
                        name = str( getattr( object, 
                                           self.factory.page_name[1:], '???' ) )
                    dock_control.name = name
                    self.update_layout()
                break

    #---------------------------------------------------------------------------
    #  Creates a DockControl for a specified object:
    #---------------------------------------------------------------------------

    def _create_page ( self, object ):
        # Create the view for the object:
        ui = object.edit_traits( parent = self.control,
                                 view   = self.factory.view,
                                 kind   = 'subpanel' )

        # Chain the sub-panel's undo history to ours:
        ui.history = self.ui.history

        # Get the name of the page being added to the notebook:
        name       = ''
        monitoring = False
        prefix     = '%s_%s_page_' % ( self.object_name, self.name )
        page_name  = self.factory.page_name
        if page_name[0:1] == '.':
            name       = getattr( object, page_name[1:], None )
            monitoring = (name is not None)
            if monitoring:
                handler_name = None
                method       = getattr( self.ui.handler, prefix + 'name', None ) 
                if method is not None:
                    handler_name = method( self.ui.info, object )
                if handler_name is not None:
                    name = handler_name
                else:
                    name = str( name ) or '???'
                object.on_trait_change( self.update_page_name, 
                                        page_name[1:], dispatch = 'ui' )
            else:
                name = ''
        elif page_name != '':
            name = page_name
        if name == '':
            name = user_name_for( object.__class__.__name__ )

        # Make sure the name is not a duplicate:
        if not monitoring:
            self._pages[ name ] = count = self._pages.get( name, 0 ) + 1
            if count > 1:
                name += (' %d' % count)

        # Return a new DockControl for the ui, and whether or not its name is
        # being monitored:
        factory = self.factory
        image   = None
        method  = getattr( self.ui.handler, prefix + 'image', None )
        if method is not None:
            image = method( self.ui.info, object )
        dock_control = DockControl( control   = ui.control,
                                    id        = str( id( ui.control ) ),
                                    name      = name,
                                    style     = factory.dock_style,
                                    image     = image,
                                    export    = factory.export,
                                    closeable = factory.deletable,
                                    dockable  = DockableListElement(
                                                    ui     = ui,
                                                    editor = self ) )
        self.set_dock_control_listener( dock_control )
        return ( dock_control, monitoring )
        
    #---------------------------------------------------------------------------
    #  Sets/Resets the listener for a DockControl being activated:  
    #---------------------------------------------------------------------------

    def set_dock_control_listener ( self, dock_control, remove = False ):
        """ Sets or removes the listener for a DockControl being activated.
        """
        dock_control.on_trait_change( self._tab_activated, 'activated',
                                      remove = remove, dispatch = 'ui' )
        
    #---------------------------------------------------------------------------
    #  Handles a notebook tab being 'activated' (i.e. clicked on) by the user:  
    #---------------------------------------------------------------------------

    def _tab_activated ( self, dock_control, name, old, new ):
        """ Handles a notebook tab being "activated" (i.e. clicked on) by the 
            user.
        """
        for a_dock_control, object, monitoring in self._uis:
            if dock_control is a_dock_control:
                self.selected = object
                break
                 
    #---------------------------------------------------------------------------
    #  Handles the 'selected' trait being changed:  
    #---------------------------------------------------------------------------

    def _selected_changed ( self, selected ):
        """ Handles the **selected** trait being changed.
        """
        for dock_control, object, monitoring in self._uis:
            if selected is object:
                dock_control.activate( False )
                break

#-------------------------------------------------------------------------------
#  'DockableListElement' class:
#-------------------------------------------------------------------------------

class DockableListElement ( DockableViewElement ):

    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # The editor this dockable item is associated with:
    editor = Instance( NotebookEditor )
        
    #---------------------------------------------------------------------------
    #  Returns whether or not it is OK to close the control, and if it is OK,
    #  then it closes the DockControl itself:    
    #---------------------------------------------------------------------------
    
    def dockable_close ( self, dock_control, force ):
        """ Returns whether it is OK to close the control.
        """
        return self.close_dock_control( dock_control, force )

    #---------------------------------------------------------------------------
    #  Closes a DockControl:
    #---------------------------------------------------------------------------

    def close_dock_control ( self, dock_control, abort ):
        """ Closes a DockControl.
        """
        if abort:
            self.editor.set_dock_control_listener( dock_control, remove = True )
            return super( DockableListElement, self ).close_dock_control(
                                                           dock_control, False )

        object = self.ui.context[ 'object' ]
        for i, value in enumerate( self.editor._uis ):
            if object is value[1]:
                value[0] = dock_control
                del self.editor.value[ i ]
                break

        return False

