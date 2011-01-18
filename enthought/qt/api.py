#------------------------------------------------------------------------------
# Copyright (c) 2010, Enthought Inc
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD license.

# 
# Author: Enthought Inc
# Description: Qt API selector. Can be used to switch between pyQt and PySide
#------------------------------------------------------------------------------

import os

from enthought.etsconfig.api import ETSConfig

qt_api = os.environ.get('QT_API', 'pyqt')

if ETSConfig.toolkit == 'qt4':
    
    if qt_api == 'pyqt':
        import sip
        sip.setapi('QString', 2)
        
        from PyQt4 import QtCore, QtGui, QtOpenGL, QtSvg, QtWebKit
        from PyQt4.Qt import QKeySequence, QTextCursor
        from PyQt4.Qt import Qt
        from PyQt4.Qt import QCoreApplication
        
        from PyQt4.QtCore import pyqtSignal as Signal
        
        def QVariant(obj=None):
            return QtCore.QVariant(obj)
        
    else:
        print "---- using PySide ----"
        from PySide import QtCore, QtGui, QtOpenGL, QtSvg, QtWebKit
        
        from PySide.QtGui import QKeySequence, QTextCursor
        from PySide.QtCore import Qt
        
        from PySide.QtCore import Signal, QCoreApplication

        def QVariant(obj=None):
            return obj
