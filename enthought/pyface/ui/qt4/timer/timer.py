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


# Major package imports.
from PyQt4 import QtCore


class Timer(QtCore.QTimer):
    """Simple subclass of QTimer that allows the user to have a function called
    periodically.  Some code assumes that this is a sub-class of wx.Timer, so
    we add a few wrapper methods to pretend it is.

    Any exceptions raised in the callable are caught.  If
    `StopIteration` is raised the timer stops.  If other exceptions are
    encountered the timer is stopped and the exception re-raised.
    """
    
    def __init__(self, millisecs, callable, *args, **kw_args):
        """ Initialize instance to invoke the given `callable` with given
        arguments and keyword args after every `millisecs` (milliseconds).
        """
        QtCore.QTimer.__init__(self)

        self.callable = callable
        self.args = args
        self.kw_args = kw_args

        self.connect(self, QtCore.SIGNAL('timeout()'), self.Notify)

        self._is_active = True
        self.start(millisecs)

    def Notify(self):
        """ Call the given callable.  Exceptions raised in the callable are
        caught.  If `StopIteration` is raised the timer stops.  If other
        exceptions are encountered the timer is stopped and the exception
        re-raised.  Note that the name of this method is part of the API
        because some code expects this to be a wx.Timer sub-class.
        """
        try:
            self.callable(*self.args, **self.kw_args)
        except StopIteration:
            self.stop()
        except:
            self.stop()
            raise

    def Start(self, millisecs=None):
        """ Emulate wx.Timer.
        """
        self._is_active = True

        if millisecs is None:
            self.start()
        else:
            self.start(millisecs)

    def Stop(self):
        """ Emulate wx.Timer.
        """
        self._is_active = False
        self.stop()

    def IsRunning(self):
        """ Emulate wx.Timer.
        """
        return self._is_active
