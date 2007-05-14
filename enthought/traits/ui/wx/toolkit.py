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
# Date: 10/13/2004
#
#  Symbols defined: GUIToolkit
#
#------------------------------------------------------------------------------
""" Defines the concrete implementations of the traits Toolkit interface for 
the wxPython user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

# Make sure that wxPython is installed
import wx

# hack: Make sure a wx.App object is created early:

_app = wx.GetApp()
if _app is None:
    _app = wx.PySimpleApp()

from enthought.traits.api \
    import HasPrivateTraits, Instance
    
from enthought.traits.trait_notifiers \
    import set_ui_handler
    
from enthought.traits.ui.api \
    import UI
    
from enthought.traits.ui.toolkit \
    import Toolkit

from enthought.util.wx.drag_and_drop \
    import PythonDropTarget, clipboard
    
from constants \
    import screen_dx, screen_dy

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

EventSuffix = {
    wx.wxEVT_LEFT_DOWN:     'left_down', 
    wx.wxEVT_LEFT_DCLICK:   'left_dclick',
    wx.wxEVT_LEFT_UP:       'left_up', 
    wx.wxEVT_MIDDLE_DOWN:   'middle_down', 
    wx.wxEVT_MIDDLE_DCLICK: 'middle_dclick', 
    wx.wxEVT_MIDDLE_UP:     'middle_up',
    wx.wxEVT_RIGHT_DOWN:    'right_down', 
    wx.wxEVT_RIGHT_DCLICK:  'right_dclick', 
    wx.wxEVT_RIGHT_UP:      'right_up', 
    wx.wxEVT_MOTION:        'mouse_move', 
    wx.wxEVT_ENTER_WINDOW:  'enter', 
    wx.wxEVT_LEAVE_WINDOW:  'leave', 
    wx.wxEVT_MOUSEWHEEL:    'mouse_wheel', 
    wx.wxEVT_PAINT:         'paint', 
}

#-------------------------------------------------------------------------------
#  Handles UI notification handler requests that occur on a thread other than
#  the UI thread:
#-------------------------------------------------------------------------------

def ui_handler ( handler, *args ):
    """ Handles UI notification handler requests that occur on a thread other 
        than the UI thread.
    """
    wx.CallAfter( handler, *args )

# Tell the traits notification handlers to use this UI handler
set_ui_handler( ui_handler )

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------
    
class GUIToolkit ( Toolkit ):
    """ Implementation class for wxPython toolkit.
    """
    #---------------------------------------------------------------------------
    #  Create wxPython specific user interfaces using information from the
    #  specified UI object:
    #---------------------------------------------------------------------------
    
    def ui_panel ( self, ui, parent ):
        """ Creates a wxPython panel-based user interface using information 
            from the specified UI object.
        """
        import ui_panel
        ui_panel.ui_panel( ui, parent )
    
    def ui_subpanel ( self, ui, parent ):
        """ Creates a wxPython subpanel-based user interface using information 
            from the specified UI object.
        """
        import ui_panel
        ui_panel.ui_subpanel( ui, parent )
    
    def ui_livemodal ( self, ui, parent ):
        """ Creates a wxPython modal "live update" dialog user interface using 
            information from the specified UI object.
        """
        import ui_live
        ui_live.ui_livemodal( ui, parent )
    
    def ui_live ( self, ui, parent ):
        """ Creates a wxPython non-modal "live update" window user interface 
            using information from the specified UI object.
        """
        import ui_live
        ui_live.ui_live( ui, parent )
    
    def ui_modal ( self, ui, parent ):
        """ Creates a wxPython modal dialog user interface using information 
            from the specified UI object.
        """
        import ui_modal
        ui_modal.ui_modal( ui, parent )
    
    def ui_nonmodal ( self, ui, parent ):
        """ Creates a wxPython non-modal dialog user interface using 
            information from the specified UI object.
        """
        import ui_modal
        ui_modal.ui_nonmodal( ui, parent )
    
    def ui_wizard ( self, ui, parent ):
        """ Creates a wxPython wizard dialog user interface using information 
            from the specified UI object.
        """
        import ui_wizard
        ui_wizard.ui_wizard( ui, parent )
        
    def view_application ( self, context, view, kind = None, handler = None,
                                     id = '', scrollable = None, args = None ):        
        """ Creates a wxPython modal dialog user interface that 
            runs as a complete application, using information from the 
            specified View object.
            
        Parameters
        ----------
        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose trait
            attributes are to be edited. If not specified, the current object is
            used.
        view : view or string
            A View object that defines a user interface for editing trait 
            attribute values. 
        kind : string
            The type of user interface window to create. See the 
            **enthought.traits.ui.view.kind_trait** trait for values and
            their meanings. If *kind* is unspecified or None, the **kind** 
            attribute of the View object is used.
        handler : Handler object
            A handler object used for event handling in the dialog box. If
            None, the default handler for Traits UI is used.
        id : string
            A unique ID for persisting preferences about this user interface,
            such as size and position. If not specified, no user preferences
            are saved.
        scrollable : Boolean
            Indicates whether the dialog box should be scrollable. When set to 
            True, scroll bars appear on the dialog box if it is not large enough
            to display all of the items in the view at one time.
        
        """
        import view_application
        return view_application.view_application( context, view, kind, handler, 
                                                  id, scrollable, args )
    
    #---------------------------------------------------------------------------
    #  Positions the associated dialog window on the display:
    #---------------------------------------------------------------------------
        
    def position ( self, ui ):
        """ Positions the associated dialog window on the display.
        """
        view   = ui.view
        window = ui.control

        # Set up the default position of the window:
        parent = window.GetParent()
        if parent is None:
           px,  py  = 0, 0
           pdx, pdy = screen_dx, screen_dy
        else:
           px,  py  = parent.GetPositionTuple()
           pdx, pdy = parent.GetSizeTuple()
        
        # Calculate the correct width and height for the window:
        cur_width, cur_height = window.GetSizeTuple() 
        width  = view.width
        height = view.height
        
        if width < 0.0:
            width = cur_width
        elif width <= 1.0:
            width = int( width * screen_dx )
        else:
            width = int( width )
            
        if height < 0.0:
            height = cur_height
        elif height <= 1.0:
            height = int( height * screen_dy )
        else:
            height = int( height )
            
        # Calculate the correct position for the window:
        x = view.x
        y = view.y
        
        if x < -99999.0:
            x = px + ((pdx - width) / 2)
        elif x <= -1.0:
            x = px + pdx - width + int( x ) + 1
        elif x < 0.0:
            x = px + pdx - width + int( x * pdx )
        elif x <= 1.0:
            x = px + int( x * pdx )
        else:
            x = int( x )
        
        if y < -99999.0:
            y = py + ((pdy - height) / 2)
        elif y <= -1.0:
            y = py + pdy - height + int( y ) + 1
        elif x < 0.0:
            y = py + pdy - height + int( y * pdy )
        elif y <= 1.0:
            y = py + int( y * pdy )
        else:
            y = int( y )
            
        # Position and size the window as requested:
        window.SetDimensions( max( 0, x ), max( 0, y ), width, height )
        
    #---------------------------------------------------------------------------
    #  Shows a 'Help' window for a specified UI and control:    
    #---------------------------------------------------------------------------
                
    def show_help ( self, ui, control ):
        """ Shows a help window for a specified UI and control.
        """
        import ui_panel
        ui_panel.show_help( ui, control )
        
    #---------------------------------------------------------------------------
    #  Saves user preference information associated with a UI window:  
    #---------------------------------------------------------------------------
                
    def save_window ( self, ui ):
        """ Saves user preference information associated with a UI window.
        """
        import helper
        
        helper.save_window( ui )

    #---------------------------------------------------------------------------
    #  Rebuilds a UI after a change to the content of the UI:  
    #---------------------------------------------------------------------------
                
    def rebuild_ui ( self, ui ):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        parent = size = None
        if ui.control is not None:
            size   = ui.control.GetSize()
            parent = ui.control._parent
            ui.dispose( abort = True )
            ui.info.ui = ui
        ui.rebuild( ui, parent )
        if parent is not None:
            ui.control.SetSize( size )
            sizer = parent.GetSizer()
            if sizer is not None:
                sizer.Add( ui.control, 1, wx.EXPAND )
        
    #---------------------------------------------------------------------------
    #  Sets the title for the UI window:    
    #---------------------------------------------------------------------------
                
    def set_title ( self, ui ):
        """ Sets the title for the UI window.
        """
        ui.control.SetTitle( ui.title )    
        
    #---------------------------------------------------------------------------
    #  Sets the icon for the UI window:    
    #---------------------------------------------------------------------------
                
    def set_icon ( self, ui ):
        """ Sets the icon for the UI window.
        """
        from enthought.pyface.image_resource import ImageResource
        
        if isinstance( ui.icon, ImageResource ):
            ui.control.SetIcon( ui.icon.create_icon() )
        
    #---------------------------------------------------------------------------
    #  Converts a keystroke event into a corresponding key name:  
    #---------------------------------------------------------------------------
                    
    def key_event_to_name ( self, event ):
        """ Converts a keystroke event into a corresponding key name.
        """
        import key_event_to_name
        
        return key_event_to_name.key_event_to_name( event )
        
    #---------------------------------------------------------------------------
    #  Hooks all interesting events for all controls in a ui so that they can
    #  be routed to the correct event handler:
    #---------------------------------------------------------------------------
                
    def hook_events ( self, ui, control, drop_target = None ):
        """ Hooks all interesting mouse events for all controls in a UI so that
        they can be routed to the correct event handler.
        """
        id            = control.GetId()
        event_handler = wx.EvtHandler()
        connect       = event_handler.Connect
        route_event   = ui.route_event
        
        connect( id, id, wx.wxEVT_LEFT_DOWN,     route_event )
        connect( id, id, wx.wxEVT_LEFT_DCLICK,   route_event )
        connect( id, id, wx.wxEVT_LEFT_UP,       route_event )
        connect( id, id, wx.wxEVT_MIDDLE_DOWN,   route_event )
        connect( id, id, wx.wxEVT_MIDDLE_DCLICK, route_event ) 
        connect( id, id, wx.wxEVT_MIDDLE_UP,     route_event )
        connect( id, id, wx.wxEVT_RIGHT_DOWN,    route_event )
        connect( id, id, wx.wxEVT_RIGHT_DCLICK,  route_event )
        connect( id, id, wx.wxEVT_RIGHT_UP,      route_event )
        connect( id, id, wx.wxEVT_MOTION,        route_event )
        connect( id, id, wx.wxEVT_ENTER_WINDOW,  route_event )
        connect( id, id, wx.wxEVT_LEAVE_WINDOW,  route_event )
        connect( id, id, wx.wxEVT_MOUSEWHEEL,    route_event )
        connect( id, id, wx.wxEVT_PAINT,         route_event )
        
        control.PushEventHandler( event_handler )
        control.SetDropTarget( PythonDropTarget( 
                                   DragHandler( ui = ui, control = control ) ) )
        
        for child in control.GetChildren():
            self.hook_events( ui, child, drop_target )
        
    #---------------------------------------------------------------------------
    #  Routes a 'hooked' event to the correct handler method:    
    #---------------------------------------------------------------------------
                
    def route_event ( self, ui, event ):
        """ Routes a hooked event to the correct handler method.
        """
        suffix  = EventSuffix[ event.GetEventType() ]
        control = event.GetEventObject()
        handler = ui.handler
        method  = None
        
        owner   = getattr( control, '_owner', None )
        if owner is not None:
            method = getattr( handler, 'on_%s_%s' % ( owner.get_id(), suffix ),
                              None )
                              
        if method is None:
            method = getattr( handler, 'on_%s' % suffix, None )
            
        if method is None:
            event.Skip()
        else:
            method( ui.info, owner, event )
        
    #---------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #---------------------------------------------------------------------------
        
    def color_trait ( self, *args, **traits ):
        import color_trait as ct
        return ct.WxColor( *args, **traits )
        
    def rgb_color_trait ( self, *args, **traits ):
        import rgb_color_trait as rgbct
        return rgbct.RGBColor( *args, **traits )
        
    def rgba_color_trait ( self, *args, **traits ):
        import rgba_color_trait as rgbact
        return rgbact.RGBAColor( *args, **traits )
        
    def font_trait ( self, *args, **traits ):
        import font_trait as ft
        return ft.WxFont( *args, **traits )
        
    def kiva_font_trait ( self, *args, **traits ):
        import kiva_font_trait as kft
        return kft.KivaFont( *args, **traits )
        
    #---------------------------------------------------------------------------
    #  'EditorFactory' factory methods:
    #---------------------------------------------------------------------------
    
    # Array:
    def array_editor ( self, *args, **traits ):
        import array_editor as ae
        return ae.ToolkitEditorFactory( *args, **traits )
    
    # Boolean:
    def boolean_editor ( self, *args, **traits ):
        import boolean_editor as be
        return be.ToolkitEditorFactory( *args, **traits )
        
    # Button:
    def button_editor ( self, *args, **traits ):
        import button_editor as be
        return be.ToolkitEditorFactory( *args, **traits )
        
    # Check list:
    def check_list_editor ( self, *args, **traits ):
        import check_list_editor as cle
        return cle.ToolkitEditorFactory( *args, **traits )
        
    # Code:
    def code_editor ( self, *args, **traits ):
        import code_editor as ce
        return ce.ToolkitEditorFactory( *args, **traits )
        
    # Color:
    def color_editor ( self, *args, **traits ):
        import color_editor as ce
        return ce.ToolkitEditorFactory( *args, **traits )
        
    # Compound:
    def compound_editor ( self, *args, **traits ):
        import compound_editor as ce
        return ce.ToolkitEditorFactory( *args, **traits )
        
    # Custom:
    def custom_editor ( self, *args, **traits ):
        import custom_editor as ce
        return ce.ToolkitEditorFactory( *args, **traits )
        
    # Directory:
    def directory_editor ( self, *args, **traits ):
        import directory_editor as de
        return de.ToolkitEditorFactory( *args, **traits)

    # Drop (drag and drop target):        
    def drop_editor ( self, *args, **traits ):
        import drop_editor as de
        return de.ToolkitEditorFactory( *args, **traits)

    # Drag and drop:        
    def dnd_editor ( self, *args, **traits ):
        import dnd_editor as dnd
        return dnd.ToolkitEditorFactory( *args, **traits)
        
    def enable_rgba_color_editor ( self, *args, **traits ):
        import enable_rgba_color_editor as ergbace
        return ergbace.ToolkitEditorFactory( *args, **traits )
        
    # Enum(eration):
    def enum_editor ( self, *args, **traits ):
        import enum_editor as ee
        return ee.ToolkitEditorFactory( *args, **traits )
        
    # File:
    def file_editor ( self, *args, **traits ):
        import file_editor as fe
        return fe.ToolkitEditorFactory( *args, **traits )
        
    # Font:
    def font_editor ( self, *args, **traits ):
        import font_editor as fe
        return fe.ToolkitEditorFactory( *args, **traits )
        
    # Key Binding:
    def key_binding_editor ( self, *args, **traits ):
        import key_binding_editor as kbe
        return kbe.ToolkitEditorFactory( *args, **traits )
        
    # Kiva Font:
    def kiva_font_editor ( self, *args, **traits ):
        import kiva_font_editor as kfe
        return kfe.ToolkitEditorFactory( *args, **traits )
        
    # HTML:
    def html_editor ( self, *args, **traits ):
        import html_editor as he
        return he.ToolkitEditorFactory( *args, **traits )
        
    # Image enum(eration):
    def image_enum_editor ( self, *args, **traits ):
        import image_enum_editor as iee
        return iee.ToolkitEditorFactory( *args, **traits )
        
    # Instance:
    def instance_editor ( self, *args, **traits ):
        import instance_editor as ie
        return ie.ToolkitEditorFactory( *args, **traits )
        
    # List:
    def list_editor ( self, *args, **traits ):
        import list_editor as le
        return le.ToolkitEditorFactory( *args, **traits )
        
    # Null:
    def null_editor ( self, *args, **traits ):
        import null_editor as ne
        return ne.ToolkitEditorFactory( *args, **traits )
        
    # Ordered set:
    def ordered_set_editor ( self, *args, **traits ):
        import ordered_set_editor as ose
        return ose.ToolkitEditorFactory( *args, **traits )
        
    # Plot:
    def plot_editor ( self, *args, **traits ):
        import plot_editor as pe
        return pe.ToolkitEditorFactory( *args, **traits )
        
    # Range:
    def range_editor ( self, *args, **traits ):
        import range_editor as re
        return re.ToolkitEditorFactory( *args, **traits )
        
    # RGB Color:
    def rgb_color_editor ( self, *args, **traits ):
        import rgb_color_editor as rgbce
        return rgbce.ToolkitEditorFactory( *args, **traits )
        
    # RGBA Color:
    def rgba_color_editor ( self, *args, **traits ):
        import rgba_color_editor as rgbace
        return rgbace.ToolkitEditorFactory( *args, **traits )
        
    # Set:
    def set_editor ( self, *args, **traits ):
        import set_editor as se
        return se.ToolkitEditorFactory( *args, **traits )
        
    # Shell:
    def shell_editor ( self, *args, **traits ):
        import shell_editor as se
        return se.ToolkitEditorFactory( *args, **traits )
                
    # Table:
    def table_editor ( self, *args, **traits ):
        import table_editor as te
        return te.ToolkitEditorFactory( *args, **traits )
        
    # Text:
    def text_editor ( self, *args, **traits ):
        import text_editor as te
        return te.ToolkitEditorFactory( *args, **traits )
        
    # Title:
    def title_editor ( self, *args, **traits ):
        import title_editor
        return title_editor.TitleEditor( *args, **traits )
        
    # Tree:
    def tree_editor ( self, *args, **traits ):
        import tree_editor as te
        return te.ToolkitEditorFactory( *args, **traits )
        
    # Tuple:
    def tuple_editor ( self, *args, **traits ):
        import tuple_editor as te
        return te.ToolkitEditorFactory( *args, **traits )
        
    # Value:
    def value_editor ( self, *args, **traits ):
        import value_editor as ve
        return ve.ToolkitEditorFactory( *args, **traits )
        
#-------------------------------------------------------------------------------
#  'DragHandler' class:  
#-------------------------------------------------------------------------------
                
class DragHandler ( HasPrivateTraits ):
    """ Handler for drag events.
    """
    #---------------------------------------------------------------------------
    #  Traits definitions:  
    #---------------------------------------------------------------------------
    
    # The UI associated with the drag handler
    ui = Instance( UI )
    
    # The wx control associated with the drag handler
    control = Instance( wx.Window )

#-- Drag and drop event handlers: ----------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles a Python object being dropped on the control:    
    #---------------------------------------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the window.
        """
        return self._drag_event( 'dropped_on', x, y, data, drag_result )

    #---------------------------------------------------------------------------
    #  Handles a Python object being dragged over the control:    
    #---------------------------------------------------------------------------
                
    def wx_drag_over ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        return self._drag_event( 'drag_over', x, y, data, drag_result )
        
    #---------------------------------------------------------------------------
    #  Handles a dragged Python object leaving the window:    
    #---------------------------------------------------------------------------
                
    def wx_drag_leave ( self, data ):        
        """ Handles a dragged Python object leaving the window.
        """
        return self._drag_event( 'drag_leave' )
        
    #---------------------------------------------------------------------------
    #  Handles routing a drag event to the appropriate handler:    
    #---------------------------------------------------------------------------
                
    def _drag_event ( self, suffix, x = None, y = None, data = None, 
                                    drag_result = None ):
        """ Handles routing a drag event to the appropriate handler.
        """
        control = self.control
        handler = self.ui.handler
        method  = None
        
        owner   = getattr( control, '_owner', None )
        if owner is not None:
            method = getattr( handler, 'on_%s_%s' % ( owner.get_id(), suffix ),
                              None )
                              
        if method is None:
            method = getattr( handler, 'on_%s' % suffix, None )
            
        if method is None:
            return wx.DragNone
            
        if x is None:
            result = method( self.ui.info, owner )
        else:
            result = method( self.ui.info, owner, x, y, data, drag_result )
        if result is None:
            result = drag_result
        return result
        
