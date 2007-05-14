#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 09/27/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------
""" Defines an editor used to debug UI related problems.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, Any, Instance, Property, Int, Str, List, Code, \
           View, Item, TreeEditor, TreeNodeObject, ObjectTreeNode, \
           TableEditor, Handler
    
from enthought.traits.ui.table_column \
    import ObjectColumn

from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory

from enthought.util.wx.do_later \
    import do_later
    
#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------
        
# Mapping from wxPython sizer flags to corresponding names
all_flags = [ 
    ( wx.EXPAND,                  'EXPAND' ),
    ( wx.ALL,                     'ALL' ),
    ( wx.TOP,                     'TOP' ),
    ( wx.BOTTOM,                  'BOTTOM' ),
    ( wx.LEFT,                    'LEFT' ),
    ( wx.RIGHT,                   'RIGHT' ),
    ( wx.FIXED_MINSIZE,           'FIXED_MINSIZE' ),
    ( wx.ALIGN_CENTER,            'ALIGN_CENTER' ),
    ( wx.ALIGN_RIGHT,             'ALIGN_RIGHT' ),
    ( wx.ALIGN_BOTTOM,            'ALIGN_BOTTOM' ),
    ( wx.ALIGN_CENTER_VERTICAL,   'ALIGN_CENTER_VERTICAL' ),
    ( wx.ALIGN_CENTER_HORIZONTAL, 'ALIGN_CENTER_HORIZONTAL' )
]    
                                      
#-------------------------------------------------------------------------------
#  'UIDebugEditor' class:
#-------------------------------------------------------------------------------
                               
class UIDebugEditor ( Editor ):
    """ Editor for UI debugging, which displays a button that the user can
    click to open a debugger window.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.Button( parent, -1, 'UI Debug...' )
        wx.EVT_BUTTON( parent, self.control.GetId(), self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user clicking the **UI Debug** button.
        """
        control = self.control
        while True:
            parent = control.GetParent()
            if parent is None:
                break
            control = parent
        UIDebugger(root = WXWindow( window = control ) ).edit_traits()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for UI debugging.
ToolkitEditorFactory = BasicEditorFactory( klass = UIDebugEditor )

#-------------------------------------------------------------------------------
#  'SizerItem' class:  
#-------------------------------------------------------------------------------

class WXSizerItem ( HasPrivateTraits ):
    """ Traits wrapper for a wx.SizerItem object.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # The sizer item
    item       = Instance( wx.SizerItem )
    # The class of sizer that the item is for
    kind       = Property
    # The minimum desired size for the window
    calc_min   = Property
    # The weight factor for resizing the window
    proportion = Property
    # Flags controlling alignment
    flags      = Property
    # Empty space around item
    border     = Property
    
    #---------------------------------------------------------------------------
    #  Property implementations:  
    #---------------------------------------------------------------------------
        
    def _get_kind ( self ):
        obj = self.item.GetWindow()
        if obj is not None:
            return obj.__class__.__name__
        return self.item.GetSizer().__class__.__name__
        
    def _get_calc_min ( self ):
        dx, dy = self.item.CalcMin()
        return str( ( dx, dy ) )
        
    def _get_proportion ( self ):
        return str( self.item.GetProportion() )
        
    def _get_flags ( self ):
        flags = self.item.GetFlag()
        names = []
        for bit, name in all_flags:
            if (flags & bit) == bit:
                names.append( name )
                flags &= ~bit
        if flags != 0:
            names.append( '%8X' % flags )
        return ', '.join( names )
        
    def _get_border ( self ):
        return str( self.item.GetBorder() )
        
#  Table editor to use for displaying Sizer item information 
sizer_item_table_editor = TableEditor(        
    columns = [ ObjectColumn( name = 'kind',       editable = False ),
                ObjectColumn( name = 'calc_min',   editable = False ),
                ObjectColumn( name = 'proportion', editable = False ),
                ObjectColumn( name = 'border',     editable = False ),
                ObjectColumn( name = 'flags',      editable = False ) ],
    editable     = False,
    configurable = False,
    sortable     = False
)
    
#-------------------------------------------------------------------------------
#  'WXWindow' class:  
#-------------------------------------------------------------------------------
        
class WXWindow ( TreeNodeObject ):
    """ Tree node for a wxWindow.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # The window that this is a node for
    window    = Instance( wx.Window )
    # The class name of the window, with its label appended
    name      = Property
    # Position tuple as a string
    position  = Property
    # Size tuple as a string
    size      = Property
    # Sizer class name and minimum size, as a string
    sizer     = Property
    # The minimum size tuple, as a string
    min_size  = Property
    # The "best acceptable" size tuple, as a string
    best_size = Property
    # List of sizer items for this window
    items     = Property( List )
    result    = Property( Code )
    evaluate  = Str
    
    #---------------------------------------------------------------------------
    #  Traits view definitions:  
    #---------------------------------------------------------------------------
        
    view = View( 'position~', 'size~', 'sizer~', 'min_size~', 'best_size~',
                 '_', Item( 'items', editor = sizer_item_table_editor ),
                 '_', 'evaluate', 'result#~', 
                 kind = 'subpanel' )
                 
    #---------------------------------------------------------------------------
    #  Handles 'evaluate' being changed:
    #---------------------------------------------------------------------------
                                  
    def _evaluate_changed ( self ):
        self.trait_property_changed( 'result', None, None )
    
    #---------------------------------------------------------------------------
    #  Implementation of the various trait properties:  
    #---------------------------------------------------------------------------
        
    def _get_name ( self ):
        w = self.window
        try:
            label = w.GetLabel()
        except:
            try:
                label = w.GetValue()
            except:
                try:
                    label = w.GetTitle()
                except:
                    label = ''
        if label != '':
            label = ' (%s)' % label
        return self.window.__class__.__name__ + label
        
    def _get_size ( self ):
        dx, dy = self.window.GetSizeTuple()
        return str( ( dx, dy ) )
        
    def _get_position ( self ):
        x, y = self.window.GetPositionTuple()
        return str( ( x, y ) )
        
    def _get_sizer ( self ):
        sizer = self.window.GetSizer()
        if sizer is None:
            return ''
        dx, dy = sizer.CalcMin()
        return '%s( %d, %d )' % ( sizer.__class__.__name__, dx, dy )
        
    def _get_min_size ( self ):
        dx, dy = self.window.GetMinSize()
        return str( ( dx, dy ) )
        
    def _get_best_size ( self ):
        dx, dy = self.window.GetBestFittingSize()
        return str( ( dx, dy ) )
                                  
    def _get_result ( self ):
        try:
            result = eval( self.evaluate, { '_':  self.window,
                                            '__': self.window.GetSizer() } )
            if isinstance( result, ( list, tuple ) ):
                return '\n'.join( [ '[%d]: %s' % ( i, str( x ) ) 
                                      for i, x in enumerate( result ) ] )
            return str( result )
        except:
            return '???'
            
    def _get_items ( self ):
        sizer = self.window.GetSizer()
        if sizer is None:
            return []
        items = []
        try:
            for i in range( 10000 ):
                items.append( WXSizerItem( item = sizer.GetItem( i ) ) )
        except:
            pass
        return items

    #---------------------------------------------------------------------------
    #  Returns whether chidren of this object are allowed or not:  
    #---------------------------------------------------------------------------

    def tno_allows_children ( self, node ):
        """ Can this object have children?
        """
        return True
    
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def tno_has_children ( self, node = None ):
        """ Does the object have children?
        """
        return (len( self.window.GetChildren() ) > 0)
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def tno_get_children ( self, node ):
        """ Gets the object's children.
        """
        return [ WXWindow( window = window ) 
                 for window in self.window.GetChildren() ]
    
#-------------------------------------------------------------------------------
#  Defines the window browser tree editor:  
#-------------------------------------------------------------------------------
        
# Window browser tree editor
window_tree_editor = TreeEditor(
    nodes = [
        ObjectTreeNode( node_for = [ WXWindow ],
                        children = 'children',
                        label    = 'name' ),
    ]
)

#-------------------------------------------------------------------------------
#  'UIDebugger' class:  
#-------------------------------------------------------------------------------

class UIDebugger ( Handler ):
    """ User interface for debugging user interfaces.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Root of a wxWindow window hierarchy
    root = Property
    
    #---------------------------------------------------------------------------
    #  Traits view definitions:  
    #---------------------------------------------------------------------------
        
    view = View( [ Item( 'root', editor    = window_tree_editor,
                                 resizable = True,
                                 id        = 'tree_editor' ),
                   '|<>' ],
                 title = 'UI Debugger',
                 id    = 'enthought.traits.ui.wx.ui_debug_editor.ui_debugger' )
    
    #---------------------------------------------------------------------------
    #  Informs the handler what the UIInfo object for a View will be:  
    #---------------------------------------------------------------------------
        
    def init_info ( self, info ):
        """ Informs the handler what the UIInfo object for a View will be.
        """
        self._info = info
        do_later( self.trait_property_changed, 'root', None, None )
        
    #---------------------------------------------------------------------------
    #  Implementation of the 'root' property:  
    #---------------------------------------------------------------------------
    
    def _get_root ( self ):
        window = self._info.ui.control
        if window is None:
            return None
            
        while window.GetParent() is not None:
            window = window.GetParent()
            
        return WXWindow( window = window )
                
#-------------------------------------------------------------------------------
#  Create export objects:
#-------------------------------------------------------------------------------

ui_debugger = UIDebugger()
    
