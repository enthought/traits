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

    def __init__(self, editor, parent=None):
        """Initialise the object."""

        QtCore.QAbstractTableModel.__init__(self, parent)

        self._editor = editor

    def data(self, mi, role):
        """Reimplemented to return the data."""

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        row = self._editor.items()[mi.row()]
        column = self._editor.columns[mi.column()]
        cell = column.get_value(row)

        if cell is None:
            return QtCore.QVariant()

        return QtCore.QVariant(cell)

    def headerData(self, section, orientation, role):
        """Reimplemented to return the header data."""

        if orientation != QtCore.Qt.Horizontal or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        return QtCore.QVariant(self._editor.columns[section].get_label())

    def rowCount(self, mi):
        """Reimplemented to return the number of rows."""

        return len(self._editor.items())

    def columnCount(self, mi):
        """Reimplemented to return the number of columns."""

        return len(self._editor.columns)
