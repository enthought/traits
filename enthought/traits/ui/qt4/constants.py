#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines constants used by the PyQt implementation of the various text
editors and text editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

_palette = QtGui.QApplication.palette()

# Default dialog title
DefaultTitle = 'Edit properties'

# Color of valid input
OKColor = _palette.color(QtGui.QPalette.Base)

# Color to highlight input errors
ErrorColor = QtGui.QColor( 255, 192, 192 )

# Color for background of read-only fields
ReadonlyColor = QtGui.QColor( 244, 243, 238 )

# Color for background of fields where objects can be dropped
DropColor = QtGui.QColor( 215, 242, 255 )

# Color for an editable field
EditableColor = _palette.color(QtGui.QPalette.Base)

# Color for background of windows (like dialog background color)
WindowColor = _palette.color(QtGui.QPalette.Window)

del _palette

# Screen size values:

_geom = QtGui.QApplication.desktop().availableGeometry()

screen_dx = _geom.width()
screen_dy = _geom.height()

del _geom
