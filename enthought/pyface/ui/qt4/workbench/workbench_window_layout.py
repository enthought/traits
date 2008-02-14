#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Standard library imports.
import logging

# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Instance, on_trait_change

# Local imports.
from editor import Editor
from split_tab_widget import SplitTabWidget
from enthought.pyface.message_dialog import error
from enthought.pyface.workbench.i_workbench_window_layout import \
     MWorkbenchWindowLayout


# Logging.
logger = logging.getLogger(__name__)


# For mapping positions relative to the editor area.
_EDIT_AREA_MAP = {
    'left':     QtCore.Qt.LeftDockWidgetArea,
    'right':    QtCore.Qt.RightDockWidgetArea,
    'top':      QtCore.Qt.TopDockWidgetArea,
    'bottom':   QtCore.Qt.BottomDockWidgetArea
}

# For mapping positions relative to another view.
_VIEW_AREA_MAP = {
    'left':     (QtCore.Qt.Horizontal, True),
    'right':    (QtCore.Qt.Horizontal, False),
    'top':      (QtCore.Qt.Vertical, True),
    'bottom':   (QtCore.Qt.Vertical, False)
}


class WorkbenchWindowLayout(MWorkbenchWindowLayout):
    """ The Qt4 implementation of the workbench window layout interface.

    See the 'IWorkbenchWindowLayout' interface for the API documentation.
    
    """

    #### Private interface ####################################################

    # The widget that implements the editor area.  We keep (and use) this
    # separate reference because we can't always assume that it has been set to
    # be the main window's central widget.
    _qt4_editor_area = Instance(SplitTabWidget)

    ###########################################################################
    # 'IWorkbenchWindowLayout' interface.
    ###########################################################################

    def activate_editor(self, editor):
        if editor.control is not None:
            editor.control.show()
            self._qt4_editor_area.setCurrentWidget(editor.control)
            editor.set_focus()

        return editor

    def activate_view(self, view):
        # FIXME v3: This probably doesn't work as expected.
        view.control.raise_()
        view.set_focus()

        return view

    def add_editor(self, editor, title):
        if editor is None:
            return None

        try:
            self._qt4_editor_area.addTab(self._qt4_get_editor_control(editor), title)
        except Exception:
            logger.exception('error creating editor control [%s]', editor.id)

        return editor

    def add_view(self, view, position, relative_to=None, size=(-1, -1)):
        if view is None:
            return None

        try:
            self._qt4_add_view(view, position, relative_to, size)
            view.visible = True
        except Exception:
            logger.exception('error creating view control [%s]', view.id)

            # Even though we caught the exception, it sometimes happens that
            # the view's control has been created as a child of the application
            # window (or maybe even the dock control).  We should destroy the
            # control to avoid bad UI effects.
            view.destroy_control()

            # Additionally, display an error message to the user.
            error(self.window.control, 'Unable to add view [%s]' % view.id,
                    'Workbench Plugin Error')

        return view

    def close_editor(self, editor):
        if editor.control is not None:
            editor.control.close()

        return editor

    def close_view(self, view):
        self.hide_view(view)

        return view

    def close(self):
        self._qt4_editor_area.setParent(None)
        self._qt4_editor_area = SplitTabWidget()

        # Delete all dock widgets.
        for v in self.window.views:
            if self.contains_view(v):
                self._qt4_delete_view_dock_widget(v)

    def create_initial_layout(self, parent):
        return self._qt4_editor_area

    def contains_view(self, view):
        return hasattr(view, '_qt4_dock')

    def hide_editor_area(self):
        self._qt4_editor_area.hide()

    def hide_view(self, view):
        view._qt4_dock.hide()
        view.visible = False

        return view

    def refresh(self):
        # Nothing to do.
        pass

    def reset_editors(self):
        self._qt4_editor_area.setCurrentIndex(0)

    def reset_views(self):
        # Qt doesn't provide information about the order of dock widgets in a
        # dock area.
        pass

    def show_editor_area(self):
        self._qt4_editor_area.show()

    def show_view(self, view):
        view._qt4_dock.show()
        view.visible = True

    #### Methods for saving and restoring the layout ##########################

    def get_view_memento(self):
        # Get the IDs of the views in the main window.  This information is
        # also in the QMainWindow state, but that is opaque.
        view_ids = [v.id for v in self.window.views if self.contains_view(v)]

        # Everything else is provided by QMainWindow.
        state = str(self.window.control.saveState())

        return (0, (view_ids, state))

    def set_view_memento(self, memento):
        version, mdata = memento

        # There has only ever been version 0 so far so check with an assert.
        assert version == 0

        # Now we know the structure of the memento we can "parse" it.
        view_ids, state = mdata

        # Get a list of all views that have dock widgets and mark them.
        dock_views = [v for v in self.window.views if self.contains_view(v)]

        for v in dock_views:
            v._qt4_gone = True

        # Create a dock window for all views that had one last time.
        for v in self.window.views:
            # Make sure this is in a known state.
            v.visible = False

            for vid in view_ids:
                if vid == v.id:
                    # Create the dock widget if needed and make sure that it is
                    # invisible so that it matches the state of the visible
                    # trait.  Things will all come right when the main window
                    # state is restored below.
                    self._qt4_create_view_dock_widget(v).setVisible(False)

                    if v in dock_views:
                        delattr(v, '_qt4_gone')

                    break

        # Remove any remain unused dock widgets.
        for v in dock_views:
            try:
                delattr(v, '_qt4_gone')
            except AttributeError:
                pass
            else:
                self._qt4_delete_view_dock_widget(v)

        # Restore the state.  This will update the view's visible trait through
        # the dock window's toggle action.
        self.window.control.restoreState(state)

    def get_editor_memento(self):
        # Get the layout of the editors.
        editor_layout = self._qt4_editor_area.saveState()

        # Get a memento for each editor that describes its contents.
        editor_references = self._get_editor_references()

        return (0, (editor_layout, editor_references))

    def set_editor_memento(self, memento):
        version, mdata = memento

        # There has only ever been version 0 so far so check with an assert.
        assert version == 0

        # Now we know the structure of the memento we can "parse" it.
        editor_layout, editor_references = mdata

        def resolve_id(id):
            # Get the memento for the editor contents (if any).
            editor_memento = editor_references.get(id)

            if editor_memento is None:
                return None

            # Create the restored editor.
            editor = self.window.editor_manager.set_editor_memento(editor_memento)

            if editor is None:
                return None

            # Save the editor.
            self.window.editors.append(editor)

            # Create the control if needed and return it.
            return self._qt4_get_editor_control(editor)

        self._qt4_editor_area.restoreState(editor_layout, resolve_id)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def __qt4_editor_area_default(self):
        """ The trait initialiser. """
        w = SplitTabWidget()

        w.connect(w, QtCore.SIGNAL('hasFocus'), self._qt4_editor_focus)

        # We are interested in focus changes but we get them from the editor
        # area rather than qApp to allow the editor area to restrict them when
        # needed.
        w.connect(w, QtCore.SIGNAL('focusChanged(QWidget *,QWidget *)'),
            self._qt4_view_focus_changed)

        return w

    def _qt4_editor_focus(self, new):
        """ Handle an editor getting the focus. """

        for editor in self.window.editors:
            editor.has_focus = (editor.control is new)

    @on_trait_change('window.active_editor')
    def _qt4_active_editor_changed(self, obj, trait_name, old, new):
        """ Handle the change of active editor. """

        # Do we need to do this verification?
        if obj is not self.window or trait_name != 'active_editor':
            return

        for editor in self.window.editors:
            if editor is old:
                self._qt4_editor_area.setActiveIcon(editor.control, QtGui.QIcon())
            elif editor is new:
                self._qt4_editor_area.setActiveIcon(editor.control)

    def _qt4_view_focus_changed(self, old, new):
        """ Handle the change of focus for a view. """

        focus_part = None

        if new is not None:
            # Handle focus changes to views.
            for view in self.window.views:
                if view.control is not None and view.control.isAncestorOf(new):
                    view.has_focus = True
                    focus_part = view
                    break

        if old is not None:
            # Handle focus changes from views.
            for view in self.window.views:
                if view is not focus_part and view.control is not None and view.control.isAncestorOf(old):
                    view.has_focus = False
                    break

    def _qt4_get_editor_control(self, editor):
        """ Create the editor control if it hasn't already been done. """

        if editor.control is None:
            self.editor_opening = editor

            # We must provide a parent (because TraitsUI checks for it when
            # deciding what sort of panel to create) but it can't be the editor
            # area (because it will be automatically added to the base
            # QSplitter).
            editor.control = editor.create_control(self.window.control)
            editor.control.setObjectName(editor.id)
            self._qt4_adjust_widget_layout(editor.control)

            def on_name_changed():
                self._qt4_editor_area.setWidgetTitle(editor.control, editor.name)

            editor.on_trait_change(on_name_changed, 'name')

            self.editor_opened = editor

        self._qt4_monitor(editor.control)

        return editor.control

    def _qt4_add_view(self, view, position, relative_to, size):
        """ Add a view. """

        dw = self._qt4_create_view_dock_widget(view, size)
        mw = self.window.control

        try:
            rel_dw = relative_to._qt4_dock
        except AttributeError:
            rel_dw = None

        if rel_dw is None:
            # If we are trying to add a view with a non-existent item, then
            # just default to the left of the editor area.
            if position == 'with':
                position = 'left'

            # Position the view relative to the editor area.
            try:
                dwa = _EDIT_AREA_MAP[position]
            except KeyError:
                raise ValueError, "unknown view position: %s" % position

            mw.addDockWidget(dwa, dw)
        elif position == 'with':
            # FIXME v3: The Qt documentation says that the second should be
            # placed above the first, but it always seems to be underneath (ie.
            # hidden) which is not what the user is expecting.
            mw.tabifyDockWidget(rel_dw, dw)
        else:
            try:
                orient, swap = _VIEW_AREA_MAP[position]
            except KeyError:
                raise ValueError, "unknown view position: %s" % position

            mw.splitDockWidget(rel_dw, dw, orient)

            # The Qt documentation implies that the layout direction can be
            # used to position the new dock widget relative to the existing one
            # but I could only get the button positions to change.  Instead we
            # move things around afterwards if required.
            if swap:
                mw.removeDockWidget(rel_dw)
                mw.splitDockWidget(dw, rel_dw, orient)
                rel_dw.show()

    def _qt4_create_view_dock_widget(self, view, size=(-1, -1)):
        """ Create a dock widget that wraps a view. """

        # See if it has already been created.
        try:
            dw = view._qt4_dock
        except AttributeError:
            dw = QtGui.QDockWidget(view.name, self.window.control)
            dw.setWidget(_ViewContainer(size, self.window.control))
            dw.setObjectName(view.id)
            dw.connect(dw.toggleViewAction(), QtCore.SIGNAL('toggled(bool)'),
                    self._qt4_handle_dock_visibility)

            # Save the dock window.
            view._qt4_dock = dw

            def on_name_changed():
                view._qt4_dock.setWindowTitle(view.name)

            view.on_trait_change(on_name_changed, 'name')

        # Make sure the view control exists.
        if view.control is None:
            # Make sure that the view knows which window it is in.
            view.window = self.window

            try:
                view.control = view.create_control(self.window.control)
            except:
                # Tidy up if the view couldn't be created.
                delattr(view, '_qt4_dock')
                dw.setParent(None)
                del dw
                raise

        self._qt4_adjust_widget_layout(view.control)
        dw.widget().setCentralWidget(view.control)

        return dw

    def _qt4_delete_view_dock_widget(self, view):
        """ Delete a view's dock widget. """

        dw = view._qt4_dock

        # Remove the view first.
        dw.setWidget(None)
        view.destroy_control()

        dw.setParent(None)
        delattr(view, '_qt4_dock')

    def _qt4_handle_dock_visibility(self, checked):
        """ Handle the visibility of a dock window changing. """

        # Find the dock window by its toggle action.
        for v in self.window.views:
            try:
                dw = v._qt4_dock
            except AttributeError:
                continue

            if dw.toggleViewAction() is dw.sender():
                v.visible = checked

    @staticmethod
    def _qt4_adjust_widget_layout(w):
        """ Adjust the layout of a widget so that it appears at the top with
        with standard margins.
        """
        lay = w.layout()

        if lay is not None:
            lay.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)

            sty = w.style()
            l = sty.pixelMetric(QtGui.QStyle.PM_LayoutLeftMargin)
            t = sty.pixelMetric(QtGui.QStyle.PM_LayoutTopMargin)
            r = sty.pixelMetric(QtGui.QStyle.PM_LayoutRightMargin)
            b = sty.pixelMetric(QtGui.QStyle.PM_LayoutBottomMargin)
            lay.setContentsMargins(l, t, r, b)

    def _qt4_monitor(self, control):
        """ Install an event filter for a view or editor control to keep an eye
        on certain events.
        """

        # Create the monitoring object if needed.
        try:
            mon = self._qt4_mon
        except AttributeError:
            mon = self._qt4_mon = _Monitor(self)

        control.installEventFilter(mon)


class _Monitor(QtCore.QObject):
    """ This class monitors a view or editor control. """

    def __init__(self, layout):
        QtCore.QObject.__init__(self, layout.window.control)

        self._layout = layout

    def eventFilter(self, obj, e):
        if isinstance(e, QtGui.QCloseEvent):
            for editor in self._layout.window.editors:
                if editor.control is obj:
                    self._layout.editor_closing = editor
                    editor.destroy_control()
                    self._layout.editor_closed = editor

                    break

        return False


class _ViewContainer(QtGui.QMainWindow):
    """ This class is a container for a view that allows an initial size
    (specified as a tuple) to be set.
    """

    def __init__(self, size, main_window):
        """ Initialise the object. """

        QtGui.QMainWindow.__init__(self)

        # Save the size and main window.
        self._width, self._height = size
        self._main_window = main_window

    def sizeHint(self):
        """ Reimplemented to return the initial size or the view's current
        size.
        """

        sh = self.centralWidget().sizeHint()

        if self._width > 0:
            if self._width > 1:
                w = self._width
            else:
                w = self._main_window.width() * self._width

            sh.setWidth(int(w))

        if self._height > 0:
            if self._height > 1:
                h = self._height
            else:
                h = self._main_window.height() * self._height

            sh.setHeight(int(h))

        return sh

    def showEvent(self, e):
        """ Reimplemented to use the view's current size once shown. """

        self._width = self._height = -1

        QtGui.QMainWindow.showEvent(self, e)

#### EOF ######################################################################
