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


class DoLaterTimer(QtCore.QTimer):

    # List of currently active timers:
    active_timers = []
    
    #---------------------------------------------------------------------------
    #  Initializes the object: 
    #---------------------------------------------------------------------------

    def __init__(self, interval, callable, args, kw_args):
        QtCore.QTimer.__init__(self)

        global active_timers
        for timer in self.active_timers:
            if ((timer.callable == callable) and
                (timer.args     == args)     and
                (timer.kw_args  == kw_args)):
                timer.start(interval)
                return

        self.active_timers.append(self)
        self.callable = callable
        self.args = args
        self.kw_args = kw_args

        self.connect(self, QtCore.SIGNAL('timeout()'), self.Notify)

        self.setSingleShot(True)
        self.start(interval)
        
    #---------------------------------------------------------------------------
    #  Handles the timer pop event:  
    #---------------------------------------------------------------------------
        
    def Notify(self):
        global active_timers
        
        self.active_timers.remove(self)
        self.callable(*self.args, **self.kw_args)
