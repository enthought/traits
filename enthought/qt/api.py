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

if ETSConfig.toolkit == 'qt4':
    
    qtapi = os.environ.get('QT_API', 'pyqt')
    if qtapi == 'pyqt':
        import sip
        sip.setapi('QString', 2)
        
        from PyQt4 import QtCore, QtGui
        from PyQt4.Qt import QKeySequence, QTextCursor
        from PyQt4.Qt import Qt
        
    else:
        from PySide import QtCore, QtGui
        
        from PySide.QtGui import QKeySequence, QTextCursor
        from PySide.QtCore import Qt
