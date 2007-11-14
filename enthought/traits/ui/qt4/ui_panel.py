#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

"""Creates a panel-based PyQt user interface for a specified UI object.
"""


import cgi
import re

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Instance

from enthought.traits.ui.api \
    import Group

from enthought.traits.trait_base \
    import enumerate

from enthought.traits.ui.undo \
    import UndoHistory

from enthought.traits.ui.help_template \
    import help_template

from enthought.traits.ui.menu \
    import UndoButton, RevertButton, HelpButton

from helper \
    import position_near, UnboundedScrollArea

from constants \
    import screen_dx, screen_dy, WindowColor

from ui_base \
    import BasePanel

from editor \
    import Editor


#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Pattern of all digits    
all_digits = re.compile(r'\d+')


#-------------------------------------------------------------------------------
#  Create the different panel-based PyQt user interfaces.
#-------------------------------------------------------------------------------

def ui_panel(ui, parent):
    """Creates a panel-based PyQt user interface for a specified UI object.
    """
    _ui_panel_for(ui, parent, True)


def ui_subpanel(ui, parent):
    """Creates a subpanel-based PyQt user interface for a specified UI object.
       A subpanel does not allow control buttons (other than those specified in
       the UI object).
    """
    _ui_panel_for(ui, parent, False)


def _ui_panel_for(ui, parent, buttons):
    """Creates a panel-based PyQt user interface for a specified UI object.
    """
    # Build the view while updates are disabled.
    parent.setUpdatesEnabled(False)
    ui.control = control = _Panel(ui, parent, buttons).control
    parent.setUpdatesEnabled(True)

    control._parent = parent
    control._object = ui.context.get('object')
    control._ui = ui

    try:
        ui.prepare_ui()
    except:
        control.setParent(None)
        del control
        ui.control = None
        ui.result = False
        raise

    ui.restore_prefs()
    ui.result = True


class _Panel(BasePanel):
    """PyQt user interface panel for Traits-based user interfaces.
    """

    def __init__(self, ui, parent, allow_buttons):
        """Initialise the object.
        """
        self.ui = ui
        history = ui.history
        view = ui.view

        # Reset any existing history listeners.
        if history is not None:
            history.on_trait_change(self._on_undoable, 'undoable', remove=True)
            history.on_trait_change(self._on_redoable, 'redoable', remove=True)
            history.on_trait_change(self._on_revertable, 'undoable',
                    remove=True)

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

        # Ensure the parent has a layout we can use.
        layout = parent.layout()

        if layout is None:
            layout = QtGui.QVBoxLayout(parent)
        elif not isinstance(layout, QtGui.QBoxLayout):
            raise TypeError, "panel parent layout must be a QBoxLayout"

        # Handle any view title.
        if view.title != "":
            layout.addWidget(heading_text(parent, text=view.title).control)

        # Create and add the panel making sure that it is a widget.
        self.control = panel(ui)

        if not isinstance(self.control, QtGui.QWidget):
            # Create a container widget and make sure it doesn't take up any
            # additional screen space.
            self.control.setMargin(0)
            w = QtGui.QWidget()
            w.setLayout(self.control)
            self.control = w

        layout.addWidget(self.control)

        # Add any buttons.
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


def panel(ui):
    """Creates a panel-based PyQt user interface for a specified UI object.
       This function does not modify the UI object passed to it.  The object
       returned may be either a widget, a layout or None.
    """
    # Bind the context values to the 'info' object:
    ui.info.bind_context()

    # Get the content that will be displayed in the user interface:
    content = ui._groups
    nr_groups = len(content)

    if nr_groups == 0:
        panel = None
    if nr_groups == 1:
        panel = _GroupPanel(content[0], ui).control
    elif nr_groups > 1:
        panel = QtGui.QTabWidget()
        _fill_panel(panel, content, ui)
        panel.ui = ui

    # If the UI is scrollable then wrap the panel in a scroll area.
    if ui.scrollable and panel is not None:
        # Make sure the panel is a widget.
        if isinstance(panel, QtGui.QLayout):
            panel.setMargin(0)
            w = QtGui.QWidget()
            w.setLayout(panel)
            panel = w

        sa = UnboundedScrollArea()
        sa.setFrameShape(QtGui.QFrame.NoFrame)
        sa.setWidget(panel)
        panel = sa

    return panel


def _fill_panel(panel, content, ui, item_handler=None):
    """Fill a page based container panel with content.
    """
    active = 0

    for index, item in enumerate(content):
        page_name = item.get_label(ui)
        if page_name == "":
           page_name = "Page %d" % index

        if isinstance(item, Group):
            if item.selected:
                active = index

            gp = _GroupPanel(item, ui, suppress_label=True)
            page = gp.control
            sub_page = gp.sub_control

            # If the result is the same type with only one page, collapse it
            # down into just the page.
            if type(sub_page) is type(panel) and sub_page.count() == 1:
                new = sub_page.widget(0)

                if isinstance(panel, QtGui.QTabWidget):
                    sub_page.removeTab(0)
                else:
                    sub_page.removeItem(0)
            elif isinstance(page, QtGui.QWidget):
                new = page
            else:
                new = QtGui.QWidget()
                new.setLayout(page)

            # Add the content.
            if isinstance(panel, QtGui.QTabWidget):
                panel.addTab(new, page_name)
            else:
                panel.addItem(new, page_name)

        else:
            # FIXME: Don't yet have an example that exercises this code.
            # Create the new page as a simple DockControl containing the
            # specified set of controls:
            sizer = wx.BoxSizer( wx.VERTICAL )
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

    panel.setCurrentIndex(active)


#-------------------------------------------------------------------------------
#  Displays a help window for the specified UI's active Group:
#-------------------------------------------------------------------------------

def show_help ( ui, button ):
    """ Displays a help window for the specified UI's active Group.
    """
    group    = ui._groups[ ui._active_group ]
    template = help_template()
    if group.help != '':
        header = template.group_help % cgi.escape( group.help )
    else:
        header = template.no_group_help
    fields = []
    for item in group.get_content( False ):
        if not item.is_spacer():
            fields.append( template.item_help % (
                           cgi.escape( item.get_label( ui ) ), 
                           cgi.escape( item.get_help( ui ) ) ) )
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


class _GroupPanel(object):
    """A sub-panel for a single group of items.  It may be either a layout or a
       widget.
    """

    def __init__(self, group, ui, suppress_label=False):
        """Initialise the object.
        """
        # Get the contents of the group:
        content = group.get_content()

        # Save these for other methods.
        self.group = group
        self.ui = ui

        # outer is the top-level widget or layout that will eventually be
        # returned.  sub is the QTabWidget or QToolBox corresponding to any
        # 'tabbed' or 'fold' layout.  It is only used to collapse nested
        # widgets.  inner is the object (not necessarily a layout) that new
        # controls should be added to.
        outer = sub = inner = None

        # Determine the horizontal/vertical orientation of the group:
        if group.orientation == 'horizontal':
            self.direction = QtGui.QBoxLayout.LeftToRight
        else:
            self.direction = QtGui.QBoxLayout.TopToBottom

        # Get the group label.
        if suppress_label:
            label = ""
        else:
            label = group.label

        # Create a border if requested.
        if group.show_border:
            outer = QtGui.QGroupBox(label)
            inner = QtGui.QBoxLayout(self.direction, outer)

        elif label != "":
            outer = inner = QtGui.QBoxLayout(self.direction)
            inner.addWidget(heading_text(None, text=label).control)

        # Add the layout specific content.
        if len(content) == 0:
            pass

        elif group.layout == 'flow':
            raise NotImplementedError, "'the 'flow' layout isn't implemented"

        elif group.layout == 'split':
            # Create the splitter.
            splitter = QtGui.QSplitter()

            if self.direction == QtGui.QBoxLayout.TopToBottom:
                splitter.setOrientation(QtCore.Qt.Vertical)

            if outer is None:
                outer = splitter
            else:
                inner.addWidget(splitter)

            # Create an editor.
            self._setup_editor(group,
                    SplitterGroupEditor(control=outer, splitter=splitter))

            self._add_splitter_items(content, splitter)

        elif group.layout in ('tabbed', 'fold'):
            if group.layout == 'tabbed':
                sub = QtGui.QTabWidget()
            else:
                sub = QtGui.QToolBox()

            _fill_panel(sub, content, self.ui, self._add_page_item)

            if outer is None:
                outer = sub
            else:
                inner.addWidget(sub)

            # Create an editor.
            self._setup_editor(group, GroupEditor(control=outer))

        else:
            # See if we need to control the visual appearence of the group.
            if group.visible_when != '' or group.enabled_when != '':
                # Make sure that outer is a widget or a layout.
                if outer is None:
                    outer = inner = QtGui.QBoxLayout(self.direction)

                # Create an editor.
                self._setup_editor(group, GroupEditor(control=outer))

            if isinstance(content[0], Group):
                layout = self._add_groups(content, inner)
            else:
                layout = self._add_items(content, inner)

            if outer is None:
                outer = layout
            elif layout is not inner:
                inner.addLayout(layout)

        # Publish the top-level widget, layout or None.
        self.control = outer

        # Publish the optional sub-control.
        self.sub_control = sub

    def _add_splitter_items(self, content, splitter):
        """Adds a set of groups or items separated by splitter bars.
        """
        for item in content:
            if isinstance(item, Group):
                panel = _GroupPanel(item, self.ui, suppress_label=True).control
            else:
                panel = self._add_items([item])

            # Add the panel to the splitter.
            if panel is not None:
                if isinstance(panel, QtGui.QLayout):
                    # A QSplitter needs a widget.
                    w = QtGui.QWidget()
                    panel.setMargin(0)
                    w.setLayout(panel)
                    panel = w

                splitter.addWidget(panel)

    def _setup_editor(self, group, editor):
        """Setup the editor for a group.
        """
        if group.id != '':
            self.ui.info.bind(group.id, editor)

        if group.visible_when != '':
            self.ui.add_visible(group.visible_when, editor)

        if group.enabled_when != '':
            self.ui.add_enabled(group.enabled_when, editor)

    def _add_page_item(self, item, layout):
        """Adds a single Item to a page based panel.
        """
        self._add_items([item], layout)

    def _add_groups(self, content, outer):
        """Adds a list of Group objects to the panel, creating a layout if
           needed.  Return the outermost layout.
        """
        # Use the existing layout if there is one.
        if outer is None:
            outer = QtGui.QBoxLayout(self.direction)

        # Process each group.
        for subgroup in content:
            panel = _GroupPanel(subgroup, self.ui).control

            if isinstance(panel, QtGui.QWidget):
                outer.addWidget(panel)
            elif isinstance(panel, QtGui.QLayout):
                outer.addLayout(panel)

        return outer

    def _add_items(self, content, outer=None):
        """Adds a list of Item objects, creating a layout if needed.  Return
           the outermost layout.
        """
        # Get local references to various objects we need:
        ui = self.ui
        info = ui.info
        handler = ui.handler

        group = self.group
        show_left = group.show_left
        padding = group.padding
        columns = group.columns

        # See if a label is needed.
        show_labels = False
        for item in content:
            show_labels |= item.show_label

        # See if a grid layout is needed.
        if show_labels or columns > 1:
            inner = QtGui.QGridLayout()

            if outer is None:
                outer = inner
            else:
                outer.addLayout(inner)

            row = 0

            if show_left:
                label_alignment = QtCore.Qt.AlignRight
                if show_labels:
                    for i in range(1, group.columns * 2, 2):
                        inner.setColumnStretch(i, 1)
            else:
                label_alignment = QtCore.Qt.AlignLeft
                if show_labels:
                    for i in range(0, group.columns * 2, 2):
                        inner.setColumnStretch(i, 1)
        else:
            # Use the existing layout if there is one.
            if outer is None:
                outer = QtGui.QBoxLayout(self.direction)

            inner = outer

            row = -1
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

            # Get the name in order to determine its type:
            name = item.name

            # Check if is a label:
            if name == '':
                label = item.label
                if label != "":
                    # If we are building a multi-column layout with labels, 
                    # just add space in the next column:
                    if cols > 1 and show_labels:
                        col += 1

                    if item.style == 'simple':
                        label = QtGui.QLabel(label)
                    else:
                        label = heading_text(None, text=label).control

                    inner.addWidget(label, row, col)

                    if item.emphasized:
                        self._add_emphasis(label)

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

                    if self.direction == QtGui.QBoxLayout.LeftToRight:
                        # Add a vertical separator:
                        line.setFrameShape(QtGui.QFrame.VLine)

                        if row < 0:
                            inner.addWidget(line)
                        else:
                            inner.addWidget(line, i, row)
                    else:
                        # Add a horizontal separator:
                        line.setFrameShape(QtGui.QFrame.HLine)

                        if row < 0:
                            inner.addWidget(line)
                        else:
                            inner.addWidget(line, row, i)

                    line.setFrameShadow(QtGui.QFrame.Sunken)

                # Continue on to the next Item in the list:
                continue

            # Convert a blank to a 5 pixel spacer:
            if name == ' ':
                name = '5'

            # Check if it is a spacer:
            if all_digits.match( name ):

                # If so, add the appropriate amount of space to the sizer:
                n = int( name )
                if self.direction == QtGui.QBoxLayout.LeftToRight:
                    inner.Add( ( n, 1 ) )
                else:
                    spacer = ( 1, n )
                    inner.Add( spacer )
                    if show_labels:
                        inner.Add( spacer )

                # Continue on to the next Item in the list:
                continue

            # Otherwise, it must be a trait Item:
            object      = eval( item.object_, globals(), ui.context )
            trait       = object.base_trait( name )
            desc        = trait.desc or ''
            fixed_width = False

            # Handle any label.
            if item.show_label:
                label = self._create_label(item, ui, desc)
                self._add_widget(inner, label, row, col, show_labels,
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

            # Create the requested type of editor from the editor factory:
            factory_method = getattr( editor_factory, item.style + '_editor' )
            editor         = factory_method( ui, object, name, item.tooltip, 
                                        None).set( 
                                 item        = item,
                                 object_name = item.object )

            # Tell editor to actually build the editing widget:
            editor.prepare(None)

            # Set the initial 'enabled' state of the editor from the factory:
            editor.enabled = editor_factory.enabled

            # Add emphasis to the editor control if requested:
            if item.emphasized:
                self._add_emphasis(editor.control)

            # Give the editor focus if it requested it:
            if item.has_focus:
                editor.control.setFocus()

            # Set up the reference to the correct 'control' to use in the 
            # following section, depending upon whether we have wrapped an
            # ImagePanel around the editor control or not:
            control = editor.control

            # Set the correct size on the control, as specified by the user:
            scrollable  = editor.scrollable
            item_width  = item.width
            item_height = item.height
            growable    = 0
            if (item_width != -1) or (item_height != -1):
                width = control.width()
                height = control.height()

                if (0.0 < item_width <= 1.0) and self.is_horizontal:
                    growable = int( 1000.0 * item_width )

                item_width = int( item_width )
                if item_width < -1:
                    item_width  = -item_width
                    fixed_width = True
                else:
                    item_width = max( item_width, width )

                if (0.0 < item_height <= 1.0) and (not self.is_horizontal):
                    growable = int( 1000.0 * item_height )

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
            if item.resizable or scrollable:
                growable = growable or 500
                self.resizable = True
            elif item.springy:    
                growable = growable or 500

            # FIXME: Need to decide what to do about springy, border_size,
            # padding, item.padding and growable.
            self._add_widget(inner, control, row, col, show_labels)

            # Save the reference to the label control (if any) in the editor:
            editor.label_control = label

        return outer

    def _add_widget(self, layout, w, row, column, show_labels, label_alignment=QtCore.Qt.AlignmentFlag(0)):
        """Adds a widget to a layout taking into account the orientation and
           the position of any labels.
        """
        if row < 0:
            # It's not a grid layout.
            if isinstance(w, QtGui.QWidget):
                layout.addWidget(w)
            else:
                layout.addLayout(w)

        else:
            if show_labels:
                # Convert the "logical" column to a "physical" one.
                column *= 2

                if (label_alignment != 0 and not self.group.show_left) or \
                   (label_alignment == 0 and self.group.show_left):
                    column += 1

            if self.direction == QtGui.QBoxLayout.LeftToRight:
                # Flip the row and column.
                row, column = column, row

            if isinstance(w, QtGui.QWidget):
                layout.addWidget(w, row, column, label_alignment)
            else:
                layout.addLayout(w, row, column, label_alignment)

    def _create_label(self, item, ui, desc, suffix = ':'):
        """Creates an item label.
        """
        label = item.get_label(ui)
        if (label == '') or (label[-1:] in '?=:;,.<>/\\"\'-+#|'):
            suffix = ''

        control = QtGui.QLabel(label + suffix)

        if item.emphasized:
            self._add_emphasis(control)

        # FIXME: Decide what to do about the help.  (The non-standard wx way,
        # What's This style help, both?)
        #wx.EVT_LEFT_UP( control, show_help_popup )
        control.help = item.get_help(ui)

        if desc != '':
            control.setToolTip('Specifies ' + desc)

        return control

    def _add_emphasis(self, control):
        """Adds emphasis to a specified control's font.
        """
        # Set the foreground colour.
        pal = QtGui.QPalette(control.palette())
        pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(0, 0, 127))
        control.setPalette(pal)

        # Set the font.
        font = QtGui.QFont(control.font())
        font.setBold(True)
        font.setPointSize(font.pointSize())
        control.setFont(font)


class GroupEditor(Editor):
    """A pseudo-editor that allows a group to be managed.
    """

    def __init__(self, **traits):
        """Initialise the object.
        """

        self.set(**traits)


class SplitterGroupEditor(GroupEditor):
    """A pseudo-editor that allows a group with a 'split' layout to be managed.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The QSplitter for the group.
    splitter = Instance(QtGui.QSplitter)

    #-- UI preference save/restore interface -----------------------------------

    def restore_prefs ( self, prefs ):
        """Restores any saved user preference information associated with the 
           editor.
        """
        if isinstance(prefs, dict):
            structure = prefs.get('structure')
        else:
            structure = prefs

        self.splitter.restoreState(structure)


    def save_prefs ( self ):
        """Returns any user preference information associated with the editor.
        """
        return {'structure': str(self.splitter.saveState())}

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


HeadingText = None

def heading_text(*args, **kw):
    """Create a PyFace HeadingText control.
    """
    global HeadingText

    if HeadingText is None:
        from enthought.pyface.api import HeadingText

    return HeadingText(*args, **kw)
