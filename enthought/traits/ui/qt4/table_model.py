#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the table model used by the table editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore


class TableModel(QtCore.QAbstractTableModel):
    """The model for table data."""

    def __init__(self, parent=None):
        """Initialise the object."""

        QtCore.QAbstractTableModel.__init__(self, parent)

    def rowCount(self, mi):
        """Reimplemented to return the number of rows."""

        return 0

    def columnCount(self, mi):
        """Reimplemented to return the number of columns."""

        return 0
