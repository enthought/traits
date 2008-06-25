#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various list editors and the list editor factory for the
    PyQt user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Trait, HasTraits, BaseTraitHandler, Range, Str, Any, Instance, \
           Property, Bool, Callable

from enthought.traits.trait_base \
    import user_name_for, enumerate, xgetattr

from enthought.traits.ui.api \
    import View, Item, EditorFactory as UIEditorFactory

from enthought.traits.ui.ui_traits \
    import style_trait, AView

from editor_factory \
    import EditorFactory

from editor \
    import Editor

from helper \
    import DockStyle, IconButton

from menu \
    import MakeMenu

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Trait whose value is a BaseTraitHandler object
handler_trait = Instance( BaseTraitHandler )

# The visible number of rows displayed
rows_trait = Range( 1, 50, 5,
                    desc = 'the number of list rows to display' )

# The visible number of columns displayed
columns_trait = Range( 1, 10, 5,
                    desc = 'the number of list columns to display' )

editor_trait = Instance( UIEditorFactory )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for list editors.
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

    # The number of list rows to display:
    rows = rows_trait

    # The number of list columns to create:
    columns = columns_trait

    # Use a notebook for a custom view?
    use_notebook = Bool(False)

    #-- Notebook Specific Traits -----------------------------------------------

    # Are notebook items deletable?
    deletable = Bool(False)

    # The DockWindow graphical theme: ignored.
    dock_theme = Any

    # Dock page style to use for each DockControl:
    dock_style = DockStyle

    # Export class for each item in a notebook:
    export = Str

    # Name of the view to use in notebook mode:
    view = AView

    # A factory function that can be used to define that actual object to be
    # edited (i.e. view_object = factory( object )):
    factory = Callable

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
                             kind        = self.style + '_editor',
                             mutable     = False )

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

    # Is the list of items being edited mutable?
    mutable = Bool( True )

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
       Add &Before     [_menu_before]: self.add_before()
       Add &After      [_menu_after]:  self.add_after()
       ---
       &Delete         [_menu_delete]: self.delete_item()
       ---
       Move &Up        [_menu_up]:     self.move_up()
       Move &Down      [_menu_down]:   self.move_down()
       Move to &Top    [_menu_top]:    self.move_top()
       Move to &Bottom [_menu_bottom]: self.move_bottom()
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
        self.control = QtGui.QScrollArea()
        self.control.setFrameShape(QtGui.QFrame.NoFrame)

        # Create a widget with a grid layout as the container.
        self._list_pane = QtGui.QWidget()
        layout = QtGui.QGridLayout(self._list_pane)
        layout.setMargin(0)

        # Remember the editor to use for each individual list item:
        editor = self.factory.editor
        if editor is None:
            editor = trait_handler.item_trait.get_editor()
        self._editor = getattr( editor, self.kind )

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait:
        self.context_object.on_trait_change( self.update_editor_item,
                               self.extended_name + '_items?', dispatch = 'ui' )
        self.set_tooltip()

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
        # Disconnect the editor from any control about to be destroyed:
        self._dispose_items()

        list_pane = self._list_pane
        layout = list_pane.layout()

        # Create all of the list item trait editors:
        trait_handler = self._trait_handler
        resizable     = ((trait_handler.minlen != trait_handler.maxlen) and
                         self.mutable)
        item_trait    = trait_handler.item_trait
        values        = self.value
        index         = 0

        is_fake       = (resizable and (len( values ) == 0))
        if is_fake:
            values = [ item_trait.default_value()[1] ]

        editor = self._editor
        # FIXME: Add support for more than one column.
        for value in values:
            if resizable:
                control = IconButton('list_editor.png', self.popup_menu)
                layout.addWidget(control, index, 0)

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
                pcontrol = QtGui.QPushButton('sample', list_pane)

            if isinstance(pcontrol, QtGui.QWidget):
                layout.addWidget(pcontrol, index, 1)
            else:
                layout.addLayout(pcontrol, index, 1)

            index += 1

        if is_fake:
           self._cur_control = control
           self.empty_list()
           control.setParent(None)

        if self.single_row:
            rows = 1
        else:
            rows = self.factory.rows

        #list_pane.SetSize( wx.Size(
        #     width + ((trait_handler.maxlen > rows) * scrollbar_dx),
        #     height * rows ) )

        # QScrollArea can have problems if the widget being scrolled is set too
        # early (ie. before it contains something).
        if self.control.widget() is None:
            self.control.setWidget(list_pane)

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
        for control in self.control.widget().children():
            if isinstance(control, QtGui.QLayout):
                continue

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
        control = IconButton('list_editor.png', self.popup_menu)
        control.is_empty = True
        proxy    = ListItemProxy( self.object, self.name, -1, None, None )
        pcontrol = QtGui.QLabel('   (Empty List)')
        pcontrol.proxy = control.proxy = proxy
        self.reload_sizer( [ ( control, pcontrol ) ] )

    #---------------------------------------------------------------------------
    #  Reloads the layout from the specified list of ( button, proxy ) pairs:
    #---------------------------------------------------------------------------

    def reload_sizer ( self, controls, extra = 0 ):
        """ Reloads the layout from the specified list of ( button, proxy )
            pairs.
        """
        layout = self._list_pane.layout()

        child = layout.takeAt(0)
        while child is not None:
            child = layout.takeAt(0)

        del child

        index = 0
        for control, pcontrol in controls:
            layout.addWidget(control)
            layout.addWidget(pcontrol)

            control.proxy.index = index
            index += 1

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

    def popup_menu (self):
        """ Displays the list editor popup menu.
        """
        self._cur_control = control = self.control.sender()
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
        menu.exec_(control.mapToGlobal(QtCore.QPoint(0, 0)))

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

    #-- Private Methods --------------------------------------------------------

    def _dispose_items ( self ):
        """ Disposes of each current list item.
        """
        list_pane = self._list_pane
        layout = list_pane.layout()

        for control in list_pane.children():
            editor = getattr( control, '_editor', None )
            if editor is not None:
                editor.dispose()
                editor.control = None
            elif control is not layout:
                control.setParent(None)

        del control

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
        self._uis = []

        # Create a tab widget to hold each separate object's view:
        self.control = QtGui.QTabWidget()
        QtCore.QObject.connect(self.control,
                QtCore.SIGNAL('currentChanged(int)'), self._tab_activated)

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

        # Create a tab page for each object in the trait's value:
        for object in self.value:
            page, view_object, monitoring = self._create_page(object)

            # Remember the page for later deletion processing:
            self._uis.append([page, object, view_object, monitoring])

    #---------------------------------------------------------------------------
    #  Handles some subset of the trait's list being updated:
    #---------------------------------------------------------------------------

    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the trait's list.
        """
        index = event.index

        # Delete the page corresponding to each removed item:
        page_name = self.factory.page_name[1:]

        for i in event.removed:
            page, _, view_object, monitoring = self._uis[index]
            if monitoring:
                view_object.on_trait_change(self.update_page_name, page_name,
                        remove=True)

            self.control.removeTab(self.control.indexOf(page))

            del self._uis[index]

        # Add a page for each added object:
        first_page = None
        for object in event.added:
            page, view_object, monitoring  = self._create_page(object)
            self._uis[index:index] = [[page, object, view_object, monitoring]]
            index += 1

            if first_page is None:
                first_page = page

        if first_page is not None:
            self.control.setCurrentWidget(first_page)

    #---------------------------------------------------------------------------
    #  Closes all currently open notebook pages:
    #---------------------------------------------------------------------------

    def close_all ( self ):
        """ Closes all currently open notebook pages.
        """
        page_name = self.factory.page_name[1:]

        for _, _, view_object, monitoring in self._uis:
            if monitoring:
                view_object.on_trait_change(self.update_page_name, page_name,
                        remove=True)

        # Reset the list of ui's and dictionary of page name counts:
        self._uis = []
        self._pages = {}

        self.control.clear()

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
    #  Handles the trait defining a particular page's name being changed:
    #---------------------------------------------------------------------------

    def update_page_name ( self, object, name, old, new ):
        """ Handles the trait defining a particular page's name being changed.
        """
        for i, value in enumerate(self._uis):
            page, user_object, _, _ = value
            if object is user_object:
                name = None
                handler = getattr(self.ui.handler,
                        '%s_%s_page_name' % (self.object_name, self.name),
                        None)

                if handler is not None:
                    name = handler(self.ui.info, object)

                if name is None:
                    name = str(xgetattr(object, self.factory.page_name[1:], '???'))
                self.control.setTabText(self.control.indexOf(page), name)
                break

    #---------------------------------------------------------------------------
    #  Creates a page for a specified object and adds it to the tab widget:
    #---------------------------------------------------------------------------

    def _create_page ( self, object ):
        # Create the view for the object:
        view_object = object
        factory = self.factory
        if factory.factory is not None:
            view_object = factory.factory(object)
        ui = view_object.edit_traits( parent = self.control,
                                 view   = factory.view,
                                 kind   = 'subpanel' ).set(
                                 parent = self.ui )

        # Get the name of the page being added to the notebook:
        name       = ''
        monitoring = False
        prefix     = '%s_%s_page_' % ( self.object_name, self.name )
        page_name  = factory.page_name
        if page_name[0:1] == '.':
            name       = xgetattr( view_object, page_name[1:], None )
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
                view_object.on_trait_change( self.update_page_name,
                                        page_name[1:], dispatch = 'ui' )
            else:
                name = ''
        elif page_name != '':
            name = page_name

        if name == '':
            name = user_name_for( view_object.__class__.__name__ )

        # Make sure the name is not a duplicate:
        if not monitoring:
            self._pages[ name ] = count = self._pages.get( name, 0 ) + 1
            if count > 1:
                name += (' %d' % count)

        # Return the control for the ui, and whether or not its name is being
        # monitored:
        image   = None
        method  = getattr( self.ui.handler, prefix + 'image', None )
        if method is not None:
            image = method( self.ui.info, object )

        if image is None:
            self.control.addTab(ui.control, name)
        else:
            self.control.addTab(ui.control, image, name)

        return (ui.control, view_object, monitoring)

    #---------------------------------------------------------------------------
    #  Handles a notebook tab being 'activated' (i.e. clicked on) by the user:
    #---------------------------------------------------------------------------

    def _tab_activated(self, idx):
        """ Handles a notebook tab being "activated" (i.e. clicked on) by the
            user.
        """
        w = self.control.widget(idx)

        for page, object, _, _ in self._uis:
            if page is w:
                self.selected = object
                break

    #---------------------------------------------------------------------------
    #  Handles the 'selected' trait being changed:
    #---------------------------------------------------------------------------

    def _selected_changed(self, selected):
        """ Handles the **selected** trait being changed.
        """
        for page, object, _, _ in self._uis:
            if selected is object:
                self.control.setCurrentWidget(page)
                break
