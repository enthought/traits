#-------------------------------------------------------------------------------
#
#  Traits UI editor for editing lists of strings.
#
#  Written by: David C. Morrill
#
#  Date: 05/08/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI editor for editing lists of strings.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, Color, Str, Int, Enum, List, Bool, Instance, Dict
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory

from enthought.pyface.image_resource \
    import ImageResource
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from alignment names to wx alignment values:
alignment_map = {
    'left':   wx.LIST_FORMAT_LEFT,
    'center': wx.LIST_FORMAT_CENTRE,
    'right':  wx.LIST_FORMAT_RIGHT
}
 
#-------------------------------------------------------------------------------
#  'ListStrAdapter' class:
#-------------------------------------------------------------------------------

class ListStrAdapter ( HasPrivateTraits ):
    """ The base class for adapting list items to values that can be edited 
        by a ListStrEditor.
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The default background color for list items:
    bg_color = Color( None )
    
    # The default text color for list items:
    text_color = Color( None )
    
    # The name of the default image to use for list items:
    image = Str
    
    # Specifies where a dropped item should be placed in the list relative to
    # the item it is dropped on:
    drop = Enum( 'after', 'before', 'replace' )
    
    #-- Adapter Methods --------------------------------------------------------
    
    def can_edit ( self, object, trait, index ):
        """ Returns whether the user can edit a specified *object.trait[index]*
            list item. A True result indicates the value can be edited, while
            a False result indicates that it cannot be edited.
        """
        return True
    
    def drag ( self, object, trait, index ):
        """ Returns the 'drag' value for a specified *object.trait[index]*
            list item. A result of *None* means that the item cannot be dragged.
        """
        return self.get_text( object, trait, index )
        
    def can_drop ( self, object, trait, index, value ):
        """ Returns whether the specified *value* can be dropped on the
            specified *object.trait[index]* list item. A value of **True** means
            the *value* can be dropped; and a value of **False** indicates that
            it cannot be dropped.
        """
        return isinstance( value, basestring )
        
    def dropped ( self, object, trait, index, value ):
        """ Returns how to handle a specified *value* being dropped on a
            specified *object.trait[index]* list item. The possible return
            values are:
                
            'replace'
                Replace the item dropped on with the specified *value*.
            'before'
                Insert the specified *value* before the dropped on item.
            'after'
                Insert the specified *value* after the dropped on item.
        """
        return self.drop
     
    def get_text ( self, object, trait, index ):
        """ Returns the text to display for a specified *object.trait[index]*
            list item. 
        """
        return getattr( object, trait )[ index ]
     
    def set_text ( self, object, trait, index, text ):
        """ Sets the text for a specified *object.trait[index]* list item to
            *text*.
        """
        getattr( object, trait )[ index ] = text
     
    def get_bg_color ( self, object, trait, index ):
        """ Returns the background color for a specified *object.trait[index]*
            list item. A result of None means use the default list item 
            background color.
        """
        if self.bg_color is None:
            return None
            
        return self.bg_color_
        
    def get_text_color ( self, object, trait, index ):
        """ Returns the text color for a specified *object.trait[index]* list
            item. A result of None means use the default list item text color. 
        """
        if self.text_color is None:
            return None
            
        return self.text_color_
        
    def get_image ( self, object, trait, index ):
        """ Returns the name of the image to use for a specified 
            *object.trait[index]* list item. A result of None means no image
            should be used. Otherwise, the result should either be the name of
            the image, or an ImageResource item specifying the image to use.
        """
        if self.image == '':
            return None
        
        return self.image

#-------------------------------------------------------------------------------
#  '_ListStrEditor' class:
#-------------------------------------------------------------------------------
                               
class _ListStrEditor ( Editor ):
    """ Traits UI editor for editing lists of strings.
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The title of the editor:
    title = Str
    
    # The current set of selected items (which one is used depends upon the 
    # initial state of the editor factory 'multi_select' trait):
    selected       = Int
    multi_selected = List( Int )

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Determine the style to use for the list control:
        factory = self.factory
        style   = wx.LC_REPORT
        
        if factory.editable:
            style |= wx.LC_EDIT_LABELS 
        
        if factory.horizontal_lines:
            style |= wx.LC_HRULES
            
        if not factory.multi_select:
            style |= wx.LC_SINGLE_SEL
            
        if (factory.title == '') and (factory.title_name == ''):
            style |= wx.LC_NO_HEADER
            
        # Create the list control:
        self.control = control = wx.ListCtrl( parent, -1, style = style )
        
        # Create the list control column:
        control.InsertColumn( 0, '', 
                              format = alignment_map[ factory.alignment ] )
        
        # Set up the list control's event handlers:
        id = control.GetId()
        wx.EVT_LIST_BEGIN_DRAG(       parent, id, self._begin_drag )
        wx.EVT_LIST_BEGIN_LABEL_EDIT( parent, id, self._begin_label_edit )
        wx.EVT_LIST_END_LABEL_EDIT(   parent, id, self._end_label_edit )
        wx.EVT_LIST_ITEM_SELECTED(    parent, id, self._item_selected )
        wx.EVT_LIST_ITEM_DESELECTED(  parent, id, self._item_selected )
        
        # Initialize the editor title:
        self.title = factory.title
        self.sync_value( factory.title_name, 'title', 'from' )
        
        # Set up the selection listener (if necessary):
        if factory.multi_select:
            self.sync_value( factory.selected, 'multi_selected', 'both',
                             is_list = True )
        else:
            self.sync_value( factory.selected, 'selected', 'both' )
        
        # Set the list control's tooltip:
        self.set_tooltip()
                        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        adapter = self.factory.adapter
        control, object, name = self.control, self.object, self.name
        control.DeleteAllItems()
        for i in range( len( self.value ) ):
            list_item = wx.ListItem()
            
            list_item.SetId( i )
            
            color = adapter.get_bg_color( object, name, i ) 
            if color is not None:
                list_item.SetBackgroundColour( color )
                
            color = adapter.get_text_color( object, name, i ) 
            if color is not None:
                list_item.SetTextColour( color )
                                    
            list_item.SetText( adapter.get_text( object, name, i ) )
            
            image = self._get_image( adapter.get_image( object, name, i ) )
            if image is not None:
                list_item.SetImage( image )
                
            control.InsertItem( list_item )
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _title_changed ( self, title ):
        """ Handles the editor title being changed.
        """
        list_item = wx.ListItem()
        list_item.SetText( title )
        self.control.SetColumn( 0, list_item ) 
        
    def _selected_changed ( self, selected ):
        """ Handles the editor's 'selected' trait being changed.
        """
        if not self._no_update:
            self.control.SetItemState( selected, wx.LIST_STATE_SELECTED, 
                                                 wx.LIST_STATE_SELECTED ) 
        
    def _multi_selected_changed ( self ):
        """ Handles the editor's 'multi_selected' trait being changed.
        """
        if not self._no_update:
            control  = self.control
            selected = self._get_selected()
            
            # Select any new items that aren't already selected:
            for index in self.selected:
                if index in selected:
                    selected.remove( index )
                else:
                    control.SetItemState( index, wx.LIST_STATE_SELECTED, 
                                                 wx.LIST_STATE_SELECTED )
                              
            # Unselect all remaining selected items that aren't selected now:
            for index in selected:
                control.SetItemState( index, 0, wx.LIST_STATE_SELECTED ) 
        
    def _multi_selected_items_changed ( self, event ):
        """ Handles the editor's 'multi_selected' trait being modified.
        """
        control = self.control
        
        # Remove all items that are no longer selected:
        for index in event.removed:
            control.SetItemState( index, 0, wx.LIST_STATE_SELECTED ) 
            
        # Select all newly added items:
        for index in event.added:
            control.SetItemState( index, wx.LIST_STATE_SELECTED, 
                                         wx.LIST_STATE_SELECTED ) 
        
    #-- List Control Event Handlers --------------------------------------------
    
    def _begin_drag ( self, event ):
        """ Handles the user beginning a drag operation with the left mouse
            button.
        """
        # fixme: NOT IMPLEMENTED YET
        pass
        
    def _begin_label_edit ( self, event ):
        """ Handles the user starting to edit an item label.
        """
        if not self.factory.adapter.can_edit( self.object, self.name, 
                                              event.GetIndex() ):
            event.Veto()
        
    def _end_label_edit ( self, event ):
        """ Handles the user finishing editing an item label.
        """
        self.factory.adapter.set_text( self.object, self.name, event.GetIndex(),
                                       event.GetText() )
       
    def _item_selected ( self, event ):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            selected = self._get_selected()
            if self.factory.multi_select:
                self.multi_selected = selected
            elif len( selected ) == 0:
                self.selected = -1
            else:
                self.selected = selected[0]
        finally:
            self._no_update = False
        
    #-- Private Methods --------------------------------------------------------
    
    def _get_image ( self, image ):
        """ Converts a user specified image to a wx.ListCtrl image index.
        """
        # fixme: NOT IMPLEMENTED YET
        return None
        
    def _get_selected ( self ):
        """ Returns a list of the indices of all currently selected list items.
        """
        selected = []
        item     = -1
        control  = self.control
        while True:
            item = control.GetNextItem( item, wx.LIST_NEXT_ALL, 
                                              wx.LIST_STATE_SELECTED )
            if item == -1:
                break;
                
            selected.append( item )
            
        return selected
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for list of string editors:
class ListStrEditor ( BasicEditorFactory ):
  
    #-- Trait Definitions ------------------------------------------------------
    
    # The editor class to be created:
    klass = _ListStrEditor
    
    # The optional extended name of the trait to synchronize the selection with:
    selected = Str
    
    # The alignment to use for list items:
    alignment = Enum( 'left', 'center', 'right' )
    
    # Can the user edit the values?
    editable = Bool( True )
                 
    # Are multiple selected items allowed?
    multi_select = Bool( False )
    
    # Should horizontal lines be drawn between items?
    horizontal_lines = Bool( False )
    
    # The title for the editor:
    title = Str
    
    # The optional extended name of the trait containing the editor title:
    title_name = Str
    
    # What type of operations are allowed on the list:
    operations = List( Enum( 'delete', 'insert', 'append', 'replace' ),
                       [ 'delete', 'insert', 'append', 'replace' ] )
           
    # The adapter from list items to editor values:                       
    adapter = Instance( ListStrAdapter, () )
                       
    # The set of images that can be used:                       
    images = Dict( Str, Instance( ImageResource ) )  
    
