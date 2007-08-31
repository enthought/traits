#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the concrete implementations of the traits Toolkit interface for
the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

# Make sure a QApplication object is created early:
if QtGui.QApplication.startingUp():
    import sys
    _app = QtGui.QApplication(sys.argv)

from enthought.traits.api \
    import HasPrivateTraits, Instance, Property, Category, cached_property, Any

from enthought.traits.trait_notifiers \
    import set_ui_handler

from enthought.traits.ui.api \
    import UI, Theme

from enthought.traits.ui.toolkit \
    import Toolkit

#from enthought.util.wx.drag_and_drop \
#    import PythonDropTarget, clipboard

from constants \
    import screen_dx, screen_dy

#-------------------------------------------------------------------------------
#  Handles UI notification handler requests that occur on a thread other than
#  the UI thread:
#-------------------------------------------------------------------------------

class _CallAfter(QtCore.QObject):
    """ This class dispatches a handler so that it executes in the main GUI
        thread (similar to the wx function).
    """

    # The list of pending calls.
    _calls = []

    # The mutex around the list of pending calls.
    _calls_mutex = QtCore.QMutex()

    def __init__(self, handler, *args):
        """ Initialise the call. """
        QtCore.QObject.__init__(self)

        # Save the details of the call.
        self._handler = handler
        self._args = args

        # Add this to the list.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Move to the main GUI thread.
        self.moveToThread(QtGui.QApplication.instance().thread())

        # Dispatch next time round the event loop.
        QtCore.QTimer.singleShot(0, self._dispatch)

    def _dispatch(self):
        """ Invoke the handler. """
        # Remove from the list.
        self._calls_mutex.lock()
        del self._calls[self._calls.index(self)]
        self._calls_mutex.unlock()

        self._handler(*self._args)


def ui_handler ( handler, *args ):
    """ Handles UI notification handler requests that occur on a thread other
        than the UI thread.
    """
    _CallAfter(handler, *args)

# Tell the traits notification handlers to use this UI handler
set_ui_handler( ui_handler )

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------

class GUIToolkit ( Toolkit ):
    """ Implementation class for PyQt toolkit.
    """
    #---------------------------------------------------------------------------
    #  Create PyQt specific user interfaces using information from the
    #  specified UI object:
    #---------------------------------------------------------------------------

    def ui_panel ( self, ui, parent ):
        """ Creates a PyQt panel-based user interface using information
            from the specified UI object.
        """
        import ui_panel
        ui_panel.ui_panel( ui, parent )

    def ui_subpanel ( self, ui, parent ):
        """ Creates a PyQt subpanel-based user interface using information
            from the specified UI object.
        """
        import ui_panel
        ui_panel.ui_subpanel( ui, parent )

    def ui_livemodal ( self, ui, parent ):
        """ Creates a PyQt modal "live update" dialog user interface using
            information from the specified UI object.
        """
        import ui_live
        ui_live.ui_livemodal( ui, parent )

    def ui_live ( self, ui, parent ):
        """ Creates a PyQt non-modal "live update" window user interface
            using information from the specified UI object.
        """
        import ui_live
        ui_live.ui_live( ui, parent )

    def ui_modal ( self, ui, parent ):
        """ Creates a PyQt modal dialog user interface using information
            from the specified UI object.
        """
        import ui_modal
        ui_modal.ui_modal( ui, parent )

    def ui_nonmodal ( self, ui, parent ):
        """ Creates a PyQt non-modal dialog user interface using
            information from the specified UI object.
        """
        import ui_modal
        ui_modal.ui_nonmodal( ui, parent )

    def ui_wizard ( self, ui, parent ):
        """ Creates a PyQt wizard dialog user interface using information
            from the specified UI object.
        """
        import ui_wizard
        ui_wizard.ui_wizard( ui, parent )

    def view_application ( self, context, view, kind = None, handler = None,
                                     id = '', scrollable = None, args = None ):
        """ Creates a PyQt modal dialog user interface that
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
        parent = window.parent()
        if parent is None:
            px = 0
            py = 0
            pdx = screen_dx
            pdy = screen_dy
        else:
            px = parent.x()
            py = parent.y()
            pdx = parent.width()
            pdy = parent.height()

        # Show the window in order to establish its size.
        window.show()

        # Calculate the correct width and height for the window:
        cur_width = window.width()
        cur_height = window.height()
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
        window.setGeometry( max( 0, x ), max( 0, y ), width, height )

    #---------------------------------------------------------------------------
    #  Shows a 'Help' window for a specified UI and control:
    #---------------------------------------------------------------------------

    def show_help ( self, ui, control ):
        """ Shows a help window for a specified UI and control.
        """
        import ui_panel
        ui_panel.show_help(ui, control)

    #---------------------------------------------------------------------------
    #  Saves user preference information associated with a UI window:
    #---------------------------------------------------------------------------

    def save_window ( self, ui ):
        """ Saves user preference information associated with a UI window.
        """
        import helper
        helper.save_window(ui)

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
        ui.control.setWindowTitle(ui.title)

    #---------------------------------------------------------------------------
    #  Sets the icon for the UI window:
    #---------------------------------------------------------------------------

    def set_icon ( self, ui ):
        """ Sets the icon for the UI window.
        """
        from enthought.pyface.image_resource import ImageResource

        if isinstance(ui.icon, ImageResource):
            ui.control.setWindowIcon(ui.icon.create_icon())

    #---------------------------------------------------------------------------
    #  Converts a keystroke event into a corresponding key name:
    #---------------------------------------------------------------------------

    def key_event_to_name ( self, event ):
        """ Converts a keystroke event into a corresponding key name.
        """
        import key_event_to_name
        return key_event_to_name.key_event_to_name( event )

    #---------------------------------------------------------------------------
    #  Destroys a specified GUI toolkit control:  
    #---------------------------------------------------------------------------
    
    def destroy_control ( self, control ):
        """ Destroys a specified GUI toolkit control.
        """
        control.deleteLater()

    #---------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #---------------------------------------------------------------------------

    def color_trait ( self, *args, **traits ):
        import color_trait as ct
        return ct.PyQtColor( *args, **traits )

    def rgb_color_trait ( self, *args, **traits ):
        import rgb_color_trait as rgbct
        return rgbct.RGBColor( *args, **traits )

    def font_trait ( self, *args, **traits ):
        import font_trait as ft
        return ft.WxFont( *args, **traits )


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
    #control = Instance( wx.Window )
    control = Any

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
        
#-------------------------------------------------------------------------------
#  Defines the extensions needed to make the generic Theme class specific to
#  PyQt:
#-------------------------------------------------------------------------------
            
#class WXTheme ( Category, Theme ):
    """ Defines the extensions needed to make the generic Theme class specific
        to PyQt.
    """
"""
    
    # The image slice used to draw the theme:
    image_slice = Property( depends_on = 'image' )
    
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_image_slice ( self ):
        from image_slice import image_slice_for
        
        if self.image is None:
            return None
            
        return image_slice_for( self.image )
"""
