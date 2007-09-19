#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Creates a panel-based PyQt user interface for a specified UI object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from PyQt4 import QtCore, QtGui

from cgi \
    import escape
    
from enthought.traits.api \
    import List, Instance
    
from enthought.traits.ui.api \
    import Group
    
from enthought.traits.trait_base \
    import user_name_for, enumerate
    
from enthought.traits.ui.undo \
    import UndoHistory
    
#from enthought.traits.ui.dockable_view_element \
#    import DockableViewElement
    
from enthought.traits.ui.help_template \
    import help_template
    
from enthought.traits.ui.menu \
    import UndoButton, RevertButton, HelpButton
    
#from enthought.pyface.sizers.flow \
#    import FlowSizer
    
from helper \
    import position_near, GroupEditor
    
from constants \
    import screen_dx, screen_dy, WindowColor
    
from ui_base \
    import BaseDialog

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Pattern of all digits    
all_digits = re.compile( r'\d+' )
        
# Global font used for emphasis
emphasis_font = None

# Global color used for emphasis
emphasis_color = QtGui.QColor( 0, 0, 127 )

#-------------------------------------------------------------------------------
#  Creates a panel-based PyQt user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_panel ( ui, parent ):
    """ Creates a panel-based PyQt user interface for a specified UI object.
    """
    ui_panel_for( ui, parent, True )

#-------------------------------------------------------------------------------
#  Creates a subpanel-based PyQt user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_subpanel ( ui, parent ):
    """ Creates a subpanel-based PyQt user interface for a specified UI 
        object. A subpanel does not allow control buttons (other than those 
        specified in the UI object).
    """
    ui_panel_for( ui, parent, False )

#-------------------------------------------------------------------------------
#  Creates a panel-based PyQt user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_panel_for ( ui, parent, buttons ):
    """ Creates a panel-based PyQt user interface for a specified UI object.
    """
    # Disable screen updates on the parent control while we build the view:
    parent.setUpdatesEnabled(False)
    
    # Build the view:
    ui.control = control = Panel(ui, parent, buttons).control

    # Allow screen updates to occur again:
    parent.setUpdatesEnabled(True)
    
    control._parent = parent
    control._object = ui.context.get( 'object' )
    control._ui     = ui
    try:
        ui.prepare_ui()
    except:
        control.deleteLater()
        ui.control = None
        ui.result  = False
        raise
    ui.restore_prefs()
    ui.result = True
    
#-------------------------------------------------------------------------------
#  'Panel' class:
#-------------------------------------------------------------------------------

class Panel ( BaseDialog ):
    """ PyQt user interface panel for Traits-based user interfaces.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object: 
    #---------------------------------------------------------------------------
        
    def __init__ ( self, ui, parent, allow_buttons ):
        """ Initializes the object.
        """
        self.ui = ui
        history = None
        view    = ui.view
        title   = view.title
        
        # Reset any existing history listeners:
        history = ui.history
        if history is not None:
            history.on_trait_change( self._on_undoable, 
                                     'undoable', remove = True )
            history.on_trait_change( self._on_redoable, 
                                     'redoable', remove = True )
            history.on_trait_change( self._on_revertable, 
                                     'undoable', remove = True )
                                     
        # Determine if we need any buttons or an 'undo' history: 
        buttons  = [ self.coerce_button( button ) for button in view.buttons ]
        nbuttons = len( buttons )
        if nbuttons == 0:
            if view.undo:
                self.check_button( buttons, UndoButton )
            if view.revert:
                self.check_button( buttons, RevertButton )
            if view.help:
                self.check_button( buttons, HelpButton )
                
        if allow_buttons and (history is None):
            for button in buttons:
                if (self.is_button( button, 'Undo' ) or 
                    self.is_button( button, 'Revert' )):
                    history = UndoHistory()
                    break
        ui.history = history
          
        # Create a container panel to put everything in:
        cpanel = getattr( self, 'control', None )
        if cpanel is not None:
            # Clear any existing content:
            for w in cpanel.findChildren(QtGui.QWidget):
                w.setParent(None)

            layout = cpanel.layout()
        else:
            self.control = cpanel = QtGui.QWidget(parent)
            layout = None
        
        # Create the actual trait sheet panel and imbed it in a scrollable 
        # window (if requested):
        if layout is None:
            layout = QtGui.QVBoxLayout(cpanel)

        if ui.scrollable:
            sizer = wx.BoxSizer( wx.VERTICAL )
            sw    = wx.ScrolledWindow( cpanel )
            sizer.Add( panel( ui, sw ), 1, wx.EXPAND )
            
            sw.SetSizerAndFit( sizer )
            sw.SetScrollRate( 16, 16 )
            sw.SetMinSize( wx.Size( 0, 0 ) )
        else:
            sw = panel(ui, cpanel) 

        if ((title != '') and 
            (not isinstance( getattr( parent, 'owner', None ), DockWindow ))):
            layout.Add( heading_text( cpanel, text = title ).control, 0, 
                          wx.EXPAND )

        layout.addWidget(sw)
        
        if (allow_buttons and
            ((nbuttons != 1) or (not self.is_button( buttons[0], '' )))):
            # Add the special function buttons:
            layout.Add( wx.StaticLine( cpanel, -1 ), 0, wx.EXPAND )
            b_sizer = wx.BoxSizer( wx.HORIZONTAL )
            for button in buttons:
                if self.is_button( button, 'Undo' ):
                    self.undo = self.add_button( button, b_sizer, 
                                                 self._on_undo, False )
                    self.redo = self.add_button( button, b_sizer, 
                                                 self._on_redo, False, 'Redo' )
                    history.on_trait_change( self._on_undoable, 'undoable',
                                             dispatch = 'ui' )
                    history.on_trait_change( self._on_redoable, 'redoable',
                                             dispatch = 'ui' )
                elif self.is_button( button, 'Revert' ):
                    self.revert = self.add_button( button, b_sizer, 
                                                   self._on_revert, False )
                    history.on_trait_change( self._on_revertable, 'undoable',
                                             dispatch = 'ui' )
                elif self.is_button( button, 'Help' ):
                    self.add_button( button, b_sizer, self._on_help )
                elif not self.is_button( button, '' ):
                    self.add_button( button, b_sizer )
                
            layout.Add( b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )
   
    #---------------------------------------------------------------------------
    #  Handles an 'Undo' change request:
    #---------------------------------------------------------------------------
           
    def _on_undo ( self, event ):
        """ Handles a request to undo a change.
        """
        self.ui.history.undo()
    
    #---------------------------------------------------------------------------
    #  Handles a 'Redo' change request:
    #---------------------------------------------------------------------------
           
    def _on_redo ( self, event ):
        """ Handles a request to redo a change.
        """
        self.ui.history.redo()
    
    #---------------------------------------------------------------------------
    #  Handles a 'Revert' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_revert ( self, event ):
        """ Handles a request to revert all changes.
        """
        ui = self.ui
        ui.history.revert()
        ui.handler.revert( ui.info )
    
    #---------------------------------------------------------------------------
    #  Handles the 'Help' button being clicked:
    #---------------------------------------------------------------------------
           
    def _on_help ( self, event ):
        """ Handles the **Help** button being clicked.
        """
        self.ui.handler.show_help( self.ui.info, event.GetEventObject() )
            
    #-----------------------------------------------------------------------
    #  Handles the undo history 'undoable' state changing:
    #-----------------------------------------------------------------------
            
    def _on_undoable ( self, state ):
        """ Handles a change to the "undoable" state of the undo history.
        """
        self.undo.Enable( state )
            
    #---------------------------------------------------------------------------
    #  Handles the undo history 'redoable' state changing:
    #---------------------------------------------------------------------------
            
    def _on_redoable ( self, state ):
        """ Handles a change to the "redoable" state of the undo history.
        """
        self.redo.Enable( state )
            
    #---------------------------------------------------------------------------
    #  Handles the 'revert' state changing:
    #---------------------------------------------------------------------------
            
    def _on_revertable ( self, state ):
        """ Handles a change to the "revert" state.
        """
        self.revert.Enable( state )
    
#-------------------------------------------------------------------------------
#  Creates a panel-based PyQt user interface for a specified UI object:
#
#  Note: This version does not modify the UI object passed to it.
#-------------------------------------------------------------------------------

def panel ( ui, parent ):
    """ Creates a panel-based PyQt user interface for a specified UI object.
    
        This function does not modify the UI object passed to it
    """
    # Bind the context values to the 'info' object:
    ui.info.bind_context()
    
    # Get the content that will be displayed in the user interface:
    content = ui._groups
    
    # If there is 0 or 1 Groups in the content, create a single panel for it:
    if len(content) <= 1:
        panel = QtGui.QWidget(parent)

        if len(content) == 1:
            # Fill the panel with the Group's content:
            layout, _, _ = fill_panel_for_group(panel, content[0], ui)
            panel.setLayout(layout)

        # Return the panel that was created:
        return panel
        
    # Create a notebook which will contain a page for each group in the content:
    nb = create_notebook_for_items(content, ui, parent, None)
    nb.ui = ui

    # Return the notebook as the result:
    return nb
  
#-------------------------------------------------------------------------------
#  Creates a notebook and adds a list of groups or items to it as separate 
#  pages:  
#-------------------------------------------------------------------------------
                                                      
def create_notebook_for_items ( content, ui, parent, group,
                                item_handler = None, is_dock_window = False ):
    """ Creates a notebook and adds a list of groups or items to it as separate 
        pages.
    """
    if is_dock_window:
        nb = parent
    else:
        nb = QtGui.QTabWidget(parent)

    has_theme = ((group is not None) and (group.group_theme is not None))
    
    # Create a notebook page for each group or item in the content:
    active = 0
    for index, item in enumerate( content ):
        page_name = item.get_label(ui)
        if page_name == '':
           page_name = 'Page %d' % index

        if isinstance( item, Group ):
            # Create the group as a QTabWidget page:
            if item.selected:
                active = index
            sg_page, resizable, contents = \
                fill_panel_for_group( nb, item, ui, suppress_label = True,
                                                    is_dock_window = True )

            # FIXME: This is almost certainly wrong as I don't yet understand
            # the different widget structures that could be returned.
            # If the result is a QTabWidget with only one page, collapse it
            # down into just the page:
            if isinstance(contents, QtGui.QTabWidget) and contents.count() == 1:
                page = contents.widget(0)
                contents.removeTab(0)
                sg_page.setParent(None)
                sg_page = page
                
            # Add the content to the notebook as a new page:    
            nb.addTab(sg_page, page_name)
        else:
            # Create the new page as a simple DockControl containing the
            # specified set of controls:
            sizer = wx.BoxSizer( wx.VERTICAL )
            if has_theme:
                image_panel, image_sizer = add_image_panel( nb, group )
                panel = image_panel.control
                image_sizer.Add( sizer, 1, wx.EXPAND )
            else:   
                panel = QtGui.QWidget(nb)
                panel.SetSizer( sizer )
                
            pages.append( DockControl( name     = page_name,
                                       image    = item.image,
                                       id       = item.get_id(),
                                       style    = item.dock,
                                       dockable = DockableViewElement(
                                                      ui = ui, element = item ),
                                       export   = item.export,
                                       control  = panel ) )
            item_handler( item, panel, sizer )
            panel.GetSizer().Fit( panel )

    nb.setCurrentIndex(active)

    # Return the notebook as the result:
    return nb

#-------------------------------------------------------------------------------
#  Creates a themed ImagePanel for the specified group and parent window:
#-------------------------------------------------------------------------------

def add_image_panel ( window, group ):
    """ Creates a themed ImagePanel for the specified group and parent window.
    """
    from image_slice import ImagePanel
    
    image_panel = ImagePanel( theme = group.group_theme, text = group.label )
    panel       = image_panel.create_control( window )
    
    return ( image_panel, panel.GetSizer() )
    
#-------------------------------------------------------------------------------
#  Handles a notebook page being 'turned':
#-------------------------------------------------------------------------------
    
def _page_changed ( event ):
    nb = event.GetEventObject()
    nb.ui._active_group = event.GetSelection()
    
#-------------------------------------------------------------------------------
#  Displays a help window for the specified UI's active Group:
#-------------------------------------------------------------------------------
    
def show_help ( ui, button ):
    """ Displays a help window for the specified UI's active Group.
    """
    group    = ui._groups[ ui._active_group ]
    template = help_template()
    if group.help != '':
        header = template.group_help % escape( group.help )
    else:
        header = template.no_group_help
    fields = []
    for item in group.get_content( False ):
        if not item.is_spacer():
            fields.append( template.item_help % (
                           escape( item.get_label( ui ) ), 
                           escape( item.get_help( ui ) ) ) )
    html = template.group_html % ( header, '\n'.join( fields ) ) 
    HTMLHelpWindow( button, html, .25, .33 )
    
#-------------------------------------------------------------------------------
#  Displays a pop-up help window for a single trait:
#-------------------------------------------------------------------------------
    
def show_help_popup ( event ):
    """ Displays a pop-up help window for a single trait.
    """
    control  = event.GetEventObject()
    template = help_template()
    
    # Note: The following check is necessary because under Linux, we get back
    # a control which does not have the 'help' trait defined (it is the parent
    # of the object with the 'help' trait):
    help = getattr( control, 'help', None )
    if help is not None:
        html = template.item_html % ( control.GetLabel(), help )
        HTMLHelpWindow( control, html, .25, .13 )
    
#-------------------------------------------------------------------------------
#  Builds the user interface for a specified Group within a specified Panel:
#-------------------------------------------------------------------------------
    
def fill_panel_for_group ( panel, group, ui, suppress_label = False, 
                           is_dock_window = False, create_panel = False ):
    """ Builds the user interface for a specified Group within a specified 
        Panel.
    """
    fp = FillPanel( panel, group, ui, suppress_label, is_dock_window,
                    create_panel )
    return ( fp.control or fp.sizer, fp.resizable, fp.dock_contents )
    
#-------------------------------------------------------------------------------
#  'FillPanel' class:
#-------------------------------------------------------------------------------
    
class FillPanel ( object ):
    """ A subpanel for a single group of items.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, panel, group, ui, suppress_label, is_dock_window, 
                   create_panel ):
        """ Initializes the object.
        """
        # Get the contents of the group:
        content = group.get_content()
        
        # Create a group editor object if one is needed:
        self.control       = self.sizer = editor = None
        self.ui            = ui
        self.group         = group
        self.is_horizontal = (group.orientation == 'horizontal')
        layout             = group.layout
        is_splitter        = (layout == 'split')
        is_tabbed          = (layout == 'tabbed')
        id                 = group.id
        
        # Assume our contents are not resizable:
        self.resizable = False
        
        if is_dock_window and (is_splitter or is_tabbed):
            if is_splitter:
                self.dock_contents = self.add_dock_window_splitter_items( 
                                              panel, content, group )
            else:
                self.dock_contents = create_notebook_for_items( content, ui,
                                    panel, group, self.add_notebook_item, True )
                self.resizable     = True
            return
          
        theme = group.group_theme
        if (is_dock_window             or 
            create_panel               or
            (id != '')                 or
            (theme is not None)        or
            (group.visible_when != '') or
            (group.enabled_when != '')):
            if theme is not None:
                image_panel, image_sizer = add_image_panel( panel, group )
                new_panel       = image_panel.control
                suppress_label |= image_panel.can_show_text
            else:
                new_panel = QtGui.QWidget(panel)
            sizer = panel.layout()
            if sizer is None:
                sizer = QtGui.QVBoxLayout()
                panel.setLayout(sizer)
            self.control = panel = new_panel
            if is_splitter or is_tabbed:
                editor = DockWindowGroupEditor( control = panel )
            else:
                editor = GroupEditor( control = panel )
            if id != '':
                ui.info.bind( group.id, editor )
            if group.visible_when != '':
                ui.add_visible( group.visible_when, editor )
            if group.enabled_when != '':
                ui.add_enabled( group.enabled_when, editor )
                
        self.panel         = panel
        self.dock_contents = None
        
        # Determine the horizontal/vertical orientation of the group:
        if self.is_horizontal:
            orientation = QtGui.QBoxLayout.LeftToRight
        else:
            orientation = QtGui.QBoxLayout.TopToBottom

        # Set up a group with or without a border around its contents:
        label = ''
        if not suppress_label:
            label = group.label
        if group.show_border:
            box = wx.StaticBox( panel, -1, label )
            self.sizer = wx.StaticBoxSizer( box, orientation )
        else:
            if layout == 'flow':
                self.sizer = FlowSizer( orientation )
            else:
                self.sizer = QtGui.QBoxLayout(orientation)
            if label != '':
                self.sizer.addWidget(heading_text(panel, text=label).control)

        # If no sizer has been specified for the panel yet, make the new sizer 
        # the layout sizer for the panel:        
        if panel.layout() is None:
            panel.setLayout(self.sizer)

        if is_splitter:
            dw = DockWindow( panel, handler      = ui.handler,
                                    handler_args = ( ui.info, ),
                                    id           = ui.id,
                                    theme        = group.dock_theme ).control
            if editor is not None:
                editor.dock_window = dw
            dw.SetSizer( DockSizer( contents = 
                   self.add_dock_window_splitter_items( dw, content, group ) ) )
            self.sizer.Add( dw, 1, wx.EXPAND )
        elif len( content ) > 0:
            if is_tabbed:
                self.resizable = True
                dw = create_notebook_for_items( content, ui, panel, group,
                                                self.add_notebook_item )
                if editor is not None:
                    editor.dock_window = dw
                ###self.sizer.Add( dw, 1, wx.EXPAND | wx.ALL, 2 )
                self.sizer.Add( dw, 1, wx.EXPAND )
            # Check if content is all Group objects:
            elif layout == 'fold':
                self.resizable = True
                self.sizer.Add( self.create_fold_for_items( panel, content ), 
                                1, wx.EXPAND )
            elif isinstance( content[0], Group ):
                # If so, add them to the panel and exit:
                self.add_groups( content, panel )
            else:
                self.add_items( content, panel, self.sizer )

        # Pad the rest of the panel so that it absorbs any extra space.
        panel.layout().addStretch(1)
                
        # If the caller is a DockWindow, we need to define the content we are
        # adding to it:
        if is_dock_window:
            self.dock_contents = panel

        # If we are using an background image, add the sizer to the image sizer:
        if theme is not None:
            image_sizer.Add( self.sizer, 1, wx.EXPAND )
        
    #---------------------------------------------------------------------------
    #  Adds a set of groups or items separated by splitter bars to a DockWindow:    
    #---------------------------------------------------------------------------

    def add_dock_window_splitter_items ( self, window, content, group ):
        """ Adds a set of groups or items separated by splitter bars to a
            DockWindow.
        """
        contents = [ self.add_dock_window_splitter_item( window, item, group )
                     for item in content ]
           
        # Create a splitter group to hold the contents:
        result = DockSection( contents = contents, is_row = self.is_horizontal )
         
        # If nothing is resizable, then mark each DockControl as such:
        if not self.resizable:
            for item in result.get_controls():
                item.resizable = False

        # Return the DockSection we created:
        return result
        
    #---------------------------------------------------------------------------
    #  Adds a single group or item to a DockWindow:
    #---------------------------------------------------------------------------

    def add_dock_window_splitter_item ( self, window, item, group ):
        """ Adds a single group or item to a DockWindow.
        """
        if isinstance( item, Group ):
            sizer, resizable, contents = fill_panel_for_group( window,
                item, self.ui, suppress_label = True, is_dock_window = True )
            self.resizable |= resizable
            
            return contents
        
        orientation = wx.VERTICAL
        if self.is_horizontal:
            orientation = wx.HORIZONTAL
        sizer = wx.BoxSizer( orientation )
        
        if group.group_theme is not None:
            image_panel, image_sizer = add_image_panel( window, group )
            panel = image_panel.control
            image_sizer.Add( sizer, 1, wx.EXPAND )
        else:
            panel = QtGui.QWidget(window)
            panel.SetSizer( sizer )
            
        self.add_items( [ item ], panel, sizer )
        
        return DockRegion( contents = [ 
                 DockControl( name     = item.get_label( self.ui ),
                              image    = item.image,
                              id       = item.get_id(),
                              style    = item.dock,
                              dockable = DockableViewElement( 
                                             ui = self.ui, element = item ),
                              export   = item.export,
                              control  = panel ) ] )
        
    #---------------------------------------------------------------------------
    #  Adds a set of groups or items as vertical notebook pages to a vertical
    #  notebook:
    #---------------------------------------------------------------------------

    def create_fold_for_items ( self, window, content ):
        """ Adds a set of groups or items as vertical notebook pages to a 
            vertical notebook.
        """
        from themed_vertical_notebook import ThemedVerticalNotebook
        
        # Create the vertical notebook:
        nb     = ThemedVerticalNotebook( scrollable = True )
        result = nb.create_control( window )
                      
        # Create the notebook pages:
        nb.pages = [ self.create_fold_for_item( nb, item ) for item in content ]
            
        # Return the notebook we created:
        return result
        
    #---------------------------------------------------------------------------
    #  Adds a single group or item to a vertical notebook:
    #---------------------------------------------------------------------------
            
    def create_fold_for_item ( self, notebook, item ):
        """ Adds a single group or item to a vertical notebook.
        """
        # Create a new notebook page:
        page = notebook.create_page()

        # Create the page contents:
        if isinstance( item, Group ):
            panel, resizable, contents = fill_panel_for_group( page.parent,
                item, self.ui, suppress_label = True, create_panel = True )
        else:
            panel = QtGui.QWidget(page.parent)
            sizer = wx.BoxSizer( wx.VERTICAL )
            panel.SetSizer( sizer )
            self.add_items( [ item ], panel, sizer )
        
        # Set the page name and control:
        page.name    = item.get_label( self.ui )
        page.control = panel
        
        # Return the new notebook page:
        return page
        
    #---------------------------------------------------------------------------
    #  Adds a single Item to a notebook:  
    #---------------------------------------------------------------------------
    
    def add_notebook_item ( self, item, parent, sizer ):
        """ Adds a single Item to a notebook.
        """
        self.add_items( [ item ], parent, sizer )

    #---------------------------------------------------------------------------
    #  Adds a list of Group objects to the panel:
    #---------------------------------------------------------------------------
        
    def add_groups ( self, content, panel ):
        """ Adds a list of Group objects to the panel.
        """
        sizer = self.sizer
        
        # Process each group:
        for subgroup in content:
            # Add the sub-group to the panel:
            sg_sizer, sg_resizable, contents = \
                fill_panel_for_group( panel, subgroup, self.ui )
            
            # If the sub-group is resizable:
            if sg_resizable:
                
                # Then so are we:
                self.resizable = True
                
                # Add the sub-group so that it can be resized by the layout:
                sizer.Add( sg_sizer, 1, wx.EXPAND | wx.ALL, 2 )
                
            else:
                #style    = wx.EXPAND | wx.ALL
                #growable = 0
                #if self.is_horizontal:
                #    if subgroup.springy:
                #        growable = 1
                #    if subgroup.orientation == 'horizontal':
                #        style |= wx.ALIGN_CENTER_VERTICAL
                #sizer.Add( sg_sizer, growable, style, 2 )
                # FIXME: Try and account for the above.
                sizer.addLayout(sg_sizer)
        
    #---------------------------------------------------------------------------
    #  Adds a list of Item objects to the panel:
    #---------------------------------------------------------------------------
        
    def add_items ( self, content, panel, sizer ):
        """ Adds a list of Item objects to the panel.
        """
        # Get local references to various objects we need:
        ui = self.ui
        info = ui.info
        handler = ui.handler
        
        group = self.group
        show_left = group.show_left
        padding = group.padding
        columns = group.columns

        show_labels = False
        for item in content:
            show_labels |= item.show_label

        if show_labels or columns > 1:
            row = 0
            item_sizer = QtGui.QGridLayout()

            if show_left:
                label_alignment = QtCore.Qt.AlignRight
                if show_labels:
                    for i in range(1, group.columns * 2, 2):
                        item_sizer.setColumnStretch(i, 1)
            else:
                label_alignment = QtCore.Qt.AlignLeft
                if show_labels:
                    for i in range(0, group.columns * 2, 2):
                        item_sizer.setColumnStretch(i, 1)

            sizer.addLayout(item_sizer)
        else:
            # Otherwise, the current sizer will work as is:
            row = -1
            item_sizer = sizer
            label_alignment = 0
            
        # Process each Item in the list:
        col = -1

        for item in content:

            # Keep a track of the current logical row and column unless the
            # layout is not a grid.
            col += 1

            if row >= 0 and col >= columns:
                col = 0
                row += 1
            
            # Get the item theme (if any):
            theme = item.item_theme
            
            # Get the name in order to determine its type:
            name = item.name
            
            # Check if is a label:
            if name == '':
                label = item.label
                if label != '':
                    # If we are building a multi-column layout with labels, 
                    # just add space in the next column:
                    if cols > 1 and show_labels:
                        col += 1

                    if theme is not None:
                        from image_slice import ImageText

                        label = ImageText( panel, theme, label )
                        item_sizer.Add( label, 0, wx.EXPAND )
                    elif item.style == 'simple':
                        # Add a simple text label:
                        label = QtGui.QLabel(label, panel)
                        item_sizer.addWidget(label, row, col)
                    else:
                        # Add the label to the sizer:
                        label = heading_text( panel, text = label ).control
                        item_sizer.Add( label, 0, 
                                        wx.TOP | wx.BOTTOM | wx.EXPAND, 3 )
                                        
                    if item.emphasized:
                        self._add_emphasis( label )
                        
                # Continue on to the next Item in the list:
                continue
            
            # Check if it is a separator:
            if name == '_':
                cols = columns

                # See if the layout is a grid.
                if row >= 0:
                    # Move to the start of the next row if necessary.
                    if col > 0:
                        col = 0
                        row += 1

                    # Skip the row we are about to do.
                    row += 1

                    # Allow for the columns.
                    if show_labels:
                        cols *= 2

                for i in range(cols):
                    line = QtGui.QFrame()

                    if self.is_horizontal:
                        # Add a vertical separator:
                        line.setFrameShape(QtGui.QFrame.VLine)

                        if row < 0:
                            item_sizer.addWidget(line)
                        else:
                            item_sizer.addWidget(line, i, row)
                    else:
                        # Add a horizontal separator:
                        line.setFrameShape(QtGui.QFrame.HLine)

                        if row < 0:
                            item_sizer.addWidget(line)
                        else:
                            item_sizer.addWidget(line, row, i)

                # Continue on to the next Item in the list:
                continue
               
            # Convert a blank to a 5 pixel spacer:
            if name == ' ':
                name = '5'
               
            # Check if it is a spacer:
            if all_digits.match( name ):
                
                # If so, add the appropriate amount of space to the sizer:
                n = int( name )
                if self.is_horizontal:
                    item_sizer.Add( ( n, 1 ) )
                else:
                    spacer = ( 1, n )
                    item_sizer.Add( spacer )
                    if show_labels:
                        item_sizer.Add( spacer )
                    
                # Continue on to the next Item in the list:
                continue
               
            # Otherwise, it must be a trait Item:
            object      = eval( item.object_, globals(), ui.context )
            trait       = object.base_trait( name )
            desc        = trait.desc or ''
            fixed_width = False
            
            # Handle any label.
            if item.show_label:
                label = self.create_label(item, ui, desc, panel)
                self._add_widget(item_sizer, label, row, col, show_labels,
                        label_alignment)
            else:
                label = None

            # Get the editor factory associated with the Item:
            editor_factory = item.editor
            if editor_factory is None:
                editor_factory = trait.get_editor()
                
                # If still no editor factory found, use a default text editor:
                if editor_factory is None:
                    from text_editor import ToolkitEditorFactory
                    editor_factory = ToolkitEditorFactory()

                # If the item has formatting traits set them in the editor
                # factory:
                if item.format_func is not None:
                    editor_factory.format_func = item.format_func
                if item.format_str != '':
                    editor_factory.format_str = item.format_str

            # Set up the background image (if used):
            item_panel = panel
            if theme is not None:
                from image_slice import ImagePanel
                
                image_panel = ImagePanel( theme = theme,
                                          text  = item.get_label( ui ) )
                item_panel  = image_panel.create_control( panel )
                    
            # Create the requested type of editor from the editor factory:
            factory_method = getattr( editor_factory, item.style + '_editor' )
            editor         = factory_method( ui, object, name, item.tooltip, 
                                        item_panel ).set( 
                                 item        = item,
                                 object_name = item.object )
                                 
            # Tell editor to actually build the editing widget:
            editor.prepare( item_panel )
            
            # Set the initial 'enabled' state of the editor from the factory:
            editor.enabled = editor_factory.enabled
            
            # Add emphasis to the editor control if requested:
            if item.emphasized:
                self._add_emphasis( editor.control )
                
            # Give the editor focus if it requested it:
            if item.has_focus:
                editor.control.SetFocus()
                
            # Set up the reference to the correct 'control' to use in the 
            # following section, depending upon whether we have wrapped an
            # ImagePanel around the editor control or not:
            control = editor.control
            if theme is None:
                width = control.width()
                height = control.height()
            else:
                item_panel.GetSizer().Add( control, 1, wx.EXPAND ) 
                control       = item_panel
                width, height = image_panel.adjusted_size
                
            # Set the correct size on the control, as specified by the user:
            scrollable  = editor.scrollable
            item_width  = item.width
            item_height = item.height
            if (item_width != -1) or (item_height != -1):
                if item_width < -1:
                    item_width  = -item_width
                    fixed_width = True
                else:
                    item_width = max( item_width, width )
                    
                if item_height < -1:
                    item_height = -item_height
                    scrollable  = False
                else:
                    item_height = max( item_height, height )
                    
                control.setMinimumWidth(item_width)
                control.setMinimumHeight(item_height)
                
            # Bind the editor into the UIInfo object name space so it can be 
            # referred to by a Handler while the user interface is active:
            id = item.id or name
            info.bind( id, editor, item.id )
            
            # Also, add the editors to the list of editors used to construct 
            # the user interface:
            ui._editors.append( editor )
            
            # If the handler wants to be notified when the editor is created, 
            # add it to the list of methods to be called when the UI is 
            # complete:
            defined = getattr( handler, id + '_defined', None )
            if defined is not None:
                ui.add_defined( defined )
            
            # If the editor is conditionally visible, add the visibility 
            # 'expression' and the editor to the UI object's list of monitored 
            # objects: 
            if item.visible_when != '':
                ui.add_visible( item.visible_when, editor )
            
            # If the editor is conditionally enabled, add the enabling 
            # 'expression' and the editor to the UI object's list of monitored 
            # objects: 
            if item.enabled_when != '':
                ui.add_enabled( item.enabled_when, editor )
            
            # Add the created editor control to the sizer with the appropriate
            # layout flags and values:
            ui._scrollable |= scrollable
            growable        = 0
            if item.resizable or scrollable:
                growable       = 1
                self.resizable = True
            elif item.springy:    
                growable = 1

            # FIXME: Need to decide what to do about springy, border_size,
            # padding and item.padding.
            self._add_widget(item_sizer, control, row, col, show_labels)

            # Save the reference to the label control (if any) in the editor:
            editor.label_control = label
                
    #---------------------------------------------------------------------------
    #  Adds a widget to a layout taking into account the orientation and the
    #  position of any labels.
    #---------------------------------------------------------------------------

    def _add_widget(self, layout, w, row, column, show_labels, label_alignment=QtCore.Qt.AlignmentFlag(0)):
        if row < 0:
            # It's not a grid layout.
            layout.addWidget(w)
        else:
            if show_labels:
                # Convert the "logical" column to a "physical" one.
                column *= 2

                if (label_alignment != 0 and not self.group.show_left) or \
                   (label_alignment == 0 and self.group.show_left):
                    column += 1

            if self.is_horizontal:
                # Flip the row and column.
                row, column = column, row

            layout.addWidget(w, row, column, label_alignment)

    #---------------------------------------------------------------------------
    #  Creates an item label:
    #---------------------------------------------------------------------------
        
    def create_label ( self, item, ui, desc, parent, suffix = ':' ):
        """ Creates an item label.
        """
        label = item.get_label( ui )
        if (label == '') or (label[-1:] in '?=:;,.<>/\\"\'-+#|'):
            suffix = ''

        theme = item.label_theme
        if theme is not None:
            from image_slice import ImageText
            
            control = ImageText( parent, theme, label + suffix )
        else:            
            control = QtGui.QLabel(label + suffix, parent)

        if item.emphasized:
            self._add_emphasis( control )

        # FIXME: Decide what to do about the help.  (The non-standard wx way,
        # What's This style help, both?)
        #wx.EVT_LEFT_UP( control, show_help_popup )
        control.help = item.get_help( ui )

        if desc != '':
            control.setToolTip('Specifies ' + desc)
            
        return control

    #---------------------------------------------------------------------------
    #  Adds 'emphasis' to a specified control:  
    #---------------------------------------------------------------------------
    
    def _add_emphasis ( self, control ):
        """ Adds emphasis to a specified control's font.
        """
        global emphasis_font
        
        control.SetForegroundColour( emphasis_color )
        if emphasis_font is None:
            font          = control.GetFont()
            emphasis_font = wx.Font( font.GetPointSize() + 1, 
                                     font.GetFamily(),
                                     font.GetStyle(),
                                     wx.BOLD )
        control.SetFont( emphasis_font )
        
#-------------------------------------------------------------------------------
#  'DockWindowGroupEditor' class:
#-------------------------------------------------------------------------------
        
class DockWindowGroupEditor ( GroupEditor ):
    """ Editor for a group which displays a DockWindow.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # DockWindow for the group
    dock_window = Instance( QtGui.QDockWidget )

    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the 
    #  editor:
    #---------------------------------------------------------------------------
            
    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the 
            editor.
        """
        if isinstance( prefs, dict ):
            structure = prefs.get( 'structure' )
        else:
            structure = prefs
        self.dock_window.GetSizer().SetStructure( self.dock_window, structure )
        self.dock_window.Layout()
            
    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------
            
    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return { 'structure': self.dock_window.GetSizer().GetStructure() }
        
    #-- End UI preference save/restore interface -------------------------------                         
    
#-------------------------------------------------------------------------------
#  'HTMLHelpWindow' class:
#-------------------------------------------------------------------------------
            
class HTMLHelpWindow ( QtGui.QLabel ):
    """ Window for displaying Traits-based help text with HTML formatting.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, parent, html, scale_dx, scale_dy ):
        """ Initializes the object.
        """
        wx.Frame.__init__( self, parent, -1, 'Help' )
        self.SetBackgroundColour( WindowColor )

        # Wrap the dialog around the image button panel:
        sizer        = wx.BoxSizer( wx.VERTICAL )
        html_control = wh.HtmlWindow( self )
        html_control.SetBorders( 2 )
        html_control.SetPage( html )
        sizer.Add( html_control, 1, wx.EXPAND )
        sizer.Add( wx.StaticLine( self, -1 ), 0, wx.EXPAND )
        b_sizer = wx.BoxSizer( wx.HORIZONTAL )
        button  = wx.Button( self, -1, 'OK' )
        wx.EVT_BUTTON( self, button.GetId(), self._on_ok )
        b_sizer.Add( button, 0 )
        sizer.Add( b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )
        self.SetSizer( sizer )
        self.SetSize( wx.Size( int( scale_dx * screen_dx ), 
                               int( scale_dy * screen_dy ) ) )
 
        # Position and show the dialog:
        position_near( parent, self, align_y = -1 )
        self.Show()
        
    #---------------------------------------------------------------------------
    #  Handles the window being closed:
    #---------------------------------------------------------------------------
        
    def _on_ok ( self, event ):
        """ Handles the window being closed.
        """
        self.Destroy()

#-------------------------------------------------------------------------------
#  Creates a PyFace HeadingText control:  
#-------------------------------------------------------------------------------
                  
# FIXME: Decide later on whether to use HeadingText.  All it is being used for
# is a different font and a gradient background image - none of which should be
# hardcoded anyway.
#HeadingText = None

#def heading_text ( *args, **kw ):
#    """ Creates a PyFace HeadingText control.
#    """
    #global HeadingText
    
    #if HeadingText is None:
    #    from enthought.pyface.heading_text import HeadingText
        
    #return HeadingText( *args, **kw )

class heading_text(object):
    def __init__(self, parent, text):
        self.control = QtGui.QLabel(text, parent)
        self.control.setFrameShadow(QtGui.QFrame.Plain)
        self.control.setFrameShape(QtGui.QFrame.Box)
