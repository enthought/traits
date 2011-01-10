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

""" Defines the stub functions used for creating concrete implementations of
    the standard EditorFactory subclasses supplied with the Traits package.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import HasPrivateTraits, TraitError

from ..trait_base import ETSConfig

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of implemented UI toolkits:
TraitUIToolkits = [ 'wx', 'qt4', 'null' ]

#-------------------------------------------------------------------------------
#  Data:
#-------------------------------------------------------------------------------

# The current GUI toolkit object being used:
_toolkit = None

#-------------------------------------------------------------------------------
#  Low-level GUI toolkit selection function:
#-------------------------------------------------------------------------------

def _import_toolkit ( name ):
    return __import__( name, globals=globals(), level=1 ).toolkit


def assert_toolkit_import(name):
    """ Raise an error if a toolkit with the given name should not be allowed
    to be imported.
    """
    if ETSConfig.toolkit and ETSConfig.toolkit != name:
        raise RuntimeError, "Importing from %s backend after selecting %s " \
                "backend!" % (name, ETSConfig.toolkit)


def toolkit_object(name, raise_exceptions=False):
    """ Return the toolkit specific object with the given name.  The name
    consists of the relative module path and the object name separated by a
    colon.
    """

    mname, oname = name.split(':')

    class Unimplemented ( object ):
        """ This is returned if an object isn't implemented by the selected
        toolkit.  It raises an exception if it is ever instantiated.
        """

        def __init__( self, *args, **kwargs ):
            raise NotImplementedError( "The %s traits backend doesn't "
                "implement %s" % ( ETSConfig.toolkit, oname ) )

    be_obj   = Unimplemented
    be_mname = toolkit().__module__.split('.')[-2] + '.' + mname
    try:
        module = __import__(
            be_mname, globals=globals(), fromlist=[oname], level=1
        )
        try:
            be_obj = getattr(module, oname)
        except AttributeError, e:
            if raise_exceptions: raise e
    except ImportError, e:
        if raise_exceptions: raise e

    return be_obj


def toolkit ( *toolkits ):
    """ Selects and returns a low-level GUI toolkit.

    Use this function to get a reference to the current toolkit.
    """

    global _toolkit
    # If _toolkit has already been set, simply return it.
    if _toolkit is not None:
        return _toolkit

    if ETSConfig.toolkit:
        # If a toolkit has already been set for ETSConfig, then use it:
        _toolkit = _import_toolkit(ETSConfig.toolkit)
        return _toolkit
    else:
        if len( toolkits ) == 0:
            toolkits = TraitUIToolkits

        for toolkit_name in toolkits:
            try:
                _toolkit = _import_toolkit( toolkit_name )
    
                # In case we have just decided on a toolkit, tell everybody else:
                ETSConfig.toolkit = toolkit_name
    
                return _toolkit
    
            except (AttributeError, ImportError):
                pass
        else:
            # Try using the null toolkit and printing a warning
            try:
                _toolkit = _import_toolkit( 'null' )
                import warnings
                warnings.warn( "Unable to import the '%s' backend for traits UI; "
                               "using the 'null' toolkit instead." % toolkit_name )
                return _toolkit
    
            except ImportError:
                raise TraitError( "Could not find any UI toolkit called '%s'" %
                                  toolkit_name )

#-------------------------------------------------------------------------------
#  'Toolkit' class (abstract base class):
#-------------------------------------------------------------------------------

class Toolkit ( HasPrivateTraits ):
    """ Abstract base class for GUI toolkits.
    """

    #---------------------------------------------------------------------------
    #  Create GUI toolkit specific user interfaces using information from the
    #  specified UI object:
    #---------------------------------------------------------------------------

    def ui_panel ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific panel-based user interface using
            information from the specified UI object.
        """
        raise NotImplementedError

    def ui_subpanel ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific subpanel-based user interface using
            information from the specified UI object.
        """
        raise NotImplementedError

    def ui_livemodal ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific modal "live update" dialog user
            interface using information from the specified UI object.
        """
        raise NotImplementedError

    def ui_live ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific non-modal "live update" window user
            interface using information from the specified UI object.
        """
        raise NotImplementedError

    def ui_modal ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific modal dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError

    def ui_nonmodal ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific non-modal dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError

    def ui_popup ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        raise NotImplementedError

    def ui_popover ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        raise NotImplementedError

    def ui_info ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific temporary "live update" popup dialog
            user interface using information from the specified UI object.
        """
        raise NotImplementedError

    def ui_wizard ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific wizard dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError

    def view_application ( self, context, view, kind = None, handler = None,
                                      id = '', scrollable = None, args = None ):
        """ Creates a GUI-toolkit-specific modal dialog user interface that
            runs as a complete application using information from the
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
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Positions the associated dialog window on the display:
    #---------------------------------------------------------------------------

    def position ( self, ui ):
        """ Positions the associated dialog window on the display.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Shows a 'Help' window for a specified UI and control:
    #---------------------------------------------------------------------------

    def show_help ( self, ui, control ):
        """ Shows a Help window for a specified UI and control.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Sets the title for the UI window:
    #---------------------------------------------------------------------------

    def set_title ( self, ui ):
        """ Sets the title for the UI window.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Sets the icon for the UI window:
    #---------------------------------------------------------------------------

    def set_icon ( self, ui ):
        """ Sets the icon for the UI window.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Saves user preference information associated with a UI window:
    #---------------------------------------------------------------------------

    def save_window ( self, ui ):
        """ Saves user preference information associated with a UI window.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Rebuilds a UI after a change to the content of the UI:
    #---------------------------------------------------------------------------

    def rebuild_ui ( self, ui ):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Converts a keystroke event into a corresponding key name:
    #---------------------------------------------------------------------------

    def key_event_to_name ( self, event ):
        """ Converts a keystroke event into a corresponding key name.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Hooks all specified events for all controls in a ui so that they can be
    #  routed to the corrent event handler:
    #---------------------------------------------------------------------------

    def hook_events ( self, ui, control, events = None, handler = None ):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Routes a 'hooked' event to the corrent handler method:
    #---------------------------------------------------------------------------

    def route_event ( self, ui, event ):
        """ Routes a "hooked" event to the corrent handler method.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Indicates that an event should continue to be processed by the toolkit
    #---------------------------------------------------------------------------

    def skip_event ( self, event ):
        """ Indicates that an event should continue to be processed by the
            toolkit.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Destroys a specified GUI toolkit control:
    #---------------------------------------------------------------------------

    def destroy_control ( self, control ):
        """ Destroys a specified GUI toolkit control.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Destroys all of the child controls of a specified GUI toolkit control:
    #---------------------------------------------------------------------------

    def destroy_children ( self, control ):
        """ Destroys all of the child controls of a specified GUI toolkit
            control.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Returns a ( width, height ) tuple containing the size of a specified
    #  toolkit image:
    #---------------------------------------------------------------------------

    def image_size ( self, image ):
        """ Returns a ( width, height ) tuple containing the size of a
            specified toolkit image.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Returns a dictionary of useful constants:
    #---------------------------------------------------------------------------

    def constants ( self ):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:

            - WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Returns a renderer used to render 'themed' table cells for a specified
    #  TableColumn object:
    #---------------------------------------------------------------------------

    def themed_cell_renderer ( self, column ):
        """ Returns a renderer used to render 'themed' table cells for a
            specified TableColum object.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #---------------------------------------------------------------------------

    def color_trait ( self, *args, **traits ):
        raise NotImplementedError

    def rgb_color_trait ( self, *args, **traits ):
        raise NotImplementedError

    def rgba_color_trait ( self, *args, **traits ):
        raise NotImplementedError

    def font_trait ( self, *args, **traits ):
        raise NotImplementedError

    def kiva_font_trait ( self, *args, **traits ):
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  'Editor' class methods:
    #---------------------------------------------------------------------------

    def ui_editor ( self ):
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  'EditorFactory' factory methods:
    #---------------------------------------------------------------------------

    def array_editor ( self, *args, **traits ):
        raise NotImplementedError

    def boolean_editor ( self, *args, **traits ):
        raise NotImplementedError

    def button_editor ( self, *args, **traits ):
        raise NotImplementedError

    def check_list_editor ( self, *args, **traits ):
        raise NotImplementedError

    def code_editor ( self, *args, **traits ):
        raise NotImplementedError

    def color_editor ( self, *args, **traits ):
        raise NotImplementedError

    def compound_editor ( self, *args, **traits ):
        raise NotImplementedError

    def custom_editor ( self, *args, **traits ):
        raise NotImplementedError

    def directory_editor ( self, *args, **traits ):
        raise NotImplementedError

    def drop_editor ( self, *args, **traits ):
        raise NotImplementedError

    def dnd_editor ( self, *args, **traits ):
        raise NotImplementedError

    def enum_editor ( self, *args, **traits ):
        raise NotImplementedError

    def file_editor ( self, *args, **traits ):
        raise NotImplementedError

    def font_editor ( self, *args, **traits ):
        raise NotImplementedError

    def key_binding_editor ( self, *args, **traits ):
        raise NotImplementedError

    def history_editor ( self, *args, **traits ):
        raise NotImplementedError

    def html_editor ( self, *args, **traits ):
        raise NotImplementedError

    def image_editor ( self, *args, **traits ):
        raise NotImplementedError

    def image_enum_editor ( self, *args, **traits ):
        raise NotImplementedError

    def instance_editor ( self, *args, **traits ):
        raise NotImplementedError

    def list_editor ( self, *args, **traits ):
        raise NotImplementedError

    def list_str_editor ( self, *args, **traits ):
        raise NotImplementedError

    def null_editor ( self, *args, **traits ):
        raise NotImplementedError

    def ordered_set_editor ( self, *args, **traits ):
        raise NotImplementedError

    def plot_editor ( self, *args, **traits ):
        raise NotImplementedError

    def range_editor ( self, *args, **traits ):
        raise NotImplementedError

    def rgb_color_editor ( self, *args, **traits ):
        raise NotImplementedError

    def rgba_color_editor ( self, *args, **traits ):
        raise NotImplementedError

    def shell_editor ( self, *args, **traits ):
        raise NotImplementedError

    def table_editor ( self, *args, **traits ):
        raise NotImplementedError

    def tabular_editor ( self, *args, **traits ):
        raise NotImplementedError

    def text_editor ( self, *args, **traits ):
        raise NotImplementedError

    def title_editor ( self, *args, **traits ):
        raise NotImplementedError

    def tree_editor ( self, *args, **traits ):
        raise NotImplementedError

    def tuple_editor ( self, *args, **traits ):
        raise NotImplementedError

    def value_editor ( self, *args, **traits ):
        raise NotImplementedError

