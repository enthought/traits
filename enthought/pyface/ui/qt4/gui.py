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
from enthought.traits.api import Bool, HasTraits, implements, Unicode

# Local imports.
from enthought.pyface.i_gui import IGUI, MGUI


# Logging.
logger = logging.getLogger(__name__)


class GUI(MGUI, HasTraits):
    """ The toolkit specific implementation of a GUI.  See the IGUI interface
    for the API documentation.
    """

    implements(IGUI)

    #### 'GUI' interface ######################################################

    busy = Bool(False)

    started = Bool(False)

    state_location = Unicode

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, splash_screen=None):
        # Display the (optional) splash screen.
        self._splash_screen = splash_screen

        if self._splash_screen is not None:
            self._splash_screen.open()

    ###########################################################################
    # 'GUI' class interface.
    ###########################################################################

    def invoke_after(cls, millisecs, callable, *args, **kw):
        _FutureCall(millisecs, callable, *args, **kw)

    invoke_after = classmethod(invoke_after)

    def invoke_later(cls, callable, *args, **kw):
        _FutureCall(0, callable, *args, **kw)

    invoke_later = classmethod(invoke_later)

    def set_trait_after(cls, millisecs, obj, trait_name, new):
        _FutureCall(millisecs, setattr, obj, trait_name, new)

    set_trait_after = classmethod(set_trait_after)

    def set_trait_later(cls, obj, trait_name, new):
        _FutureCall(0, setattr, obj, trait_name, new)

    set_trait_later = classmethod(set_trait_later)

    def process_events(allow_user_events=True):
        if allow_user_events:
            events = QtCore.QEventLoop.AllEvents
        else:
            events = QtCore.QEventLoop.ExcludeUserInputEvents

        QtCore.QCoreApplication.processEvents(events)

    process_events = staticmethod(process_events)

    def set_busy(busy=True):
        if busy:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            QtGui.QApplication.restoreOverrideCursor()

    set_busy = staticmethod(set_busy)

    ###########################################################################
    # 'GUI' interface.
    ###########################################################################

    def start_event_loop(self):
        if self._splash_screen is not None:
            self._splash_screen.close()

        # Make sure that we only set the 'started' trait after the main loop
        # has really started.
        self.set_trait_later(self, "started", True)

        # This is a hack for TraitsUI.
        QtGui.QApplication.instance()._in_event_loop = True

        logger.debug("---------- starting GUI event loop ----------")
        QtGui.QApplication.exec_()

        self.started = False

    def stop_event_loop(self):
        logger.debug("---------- stopping GUI event loop ----------")
        QtGui.QApplication.quit()

    ###########################################################################
    # Private 'GUI' interface.
    ###########################################################################

    def _busy_changed(self, new):
        """ The busy trait change handler. """

        if new:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            QtGui.QApplication.restoreOverrideCursor()


class _FutureCall(QtCore.QObject):
    """ This is a helper class that is similar to the wx FutureCall class. """

    # Keep a list of references so that they don't get garbage collected.
    _calls = []

    # Manage access to the list of instances.
    _calls_mutex = QtCore.QMutex()

    def __init__(self, ms, callable, *args, **kw):
        QtCore.QObject.__init__(self)

        # Save the arguments.
        self._callable = callable
        self._args = args
        self._kw = kw

        # Save the instance.
        self._calls_mutex.lock()
        self._calls.append(self)
        self._calls_mutex.unlock()

        # Connect to the dispatcher.
        self.connect(self, QtCore.SIGNAL('dispatch'), _dispatcher.dispatch)

        # Start the timer.
        QtCore.QTimer.singleShot(ms, self._fire)

    def _fire(self):
        # Remove the instance from the global list.
        self._calls_mutex.lock()
        del self._calls[self._calls.index(self)]
        self._calls_mutex.unlock()

        # Pass the arguments to the dispatcher so that the callable executes in
        # the right thread.
        self.emit(QtCore.SIGNAL('dispatch'), self._callable, self._args, self._kw)


class _Dispatcher(QtCore.QObject):
    """ This singleton class simply invokes a callable.  The single instance
    must be created in the GUI thread, ie. this module must be first imported
    in the GUI thread.  The class must be derived from QObject to ensure that
    the right thread is used.
    """

    def dispatch(self, callable, args, kw):
        """ Invoke a callable. """
        callable(*args, **kw)


# Create the single instance.
_dispatcher = _Dispatcher()

#### EOF ######################################################################
