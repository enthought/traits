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
import os

# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Enum, implements, Int, Unicode

# Local imports.
from enthought.pyface.i_file_dialog import IFileDialog, MFileDialog
from dialog import Dialog


class FileDialog(MFileDialog, Dialog):
    """ The toolkit specific implementation of a FileDialog.  See the
    IFileDialog interface for the API documentation.
    """

    implements(IFileDialog)

    #### 'IFileDialog' interface ##############################################

    action = Enum('open', 'save as')

    default_directory = Unicode

    default_filename = Unicode

    default_path = Unicode

    directory = Unicode

    filename = Unicode

    path = Unicode

    wildcard = Unicode

    wildcard_index = Int(0)

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        # In PyQt this is a canned dialog.
        pass

    ###########################################################################
    # 'IWindow' interface.
    ###########################################################################

    def close(self):
        # Get the path of the chosen directory.
        files = self.control.selectedFiles()

        if files:
            self.path = unicode(files[0])
        else:
            self.path = ''

        # Extract the directory and filename.
        self.directory, self.filename = os.path.split(self.path)

        # Get the index of the selected filter.
        self.wildcard_index = self.control.filters().indexOf(self.control.selectedFilter())

        # Let the window close as normal.
        super(FileDialog, self).close()

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        # If the caller provided a default path instead of a default directory
        # and filename, split the path into it directory and filename
        # components.
        if len(self.default_path) != 0 and len(self.default_directory) == 0 \
            and len(self.default_filename) == 0:
            default_directory, default_filename = os.path.split(self.default_path)
        else:
            default_directory = self.default_directory
            default_filename = self.default_filename

        # Convert the filter.
        keep = True
        filters = QtCore.QStringList()

        for f in self.wildcard.split('|'):
            if keep and f:
                filters << f

            keep = not keep

        # Set the default directory.
        if not default_directory:
            default_directory = QtCore.QDir.currentPath()

        dlg = QtGui.QFileDialog(parent, self.title, default_directory)

        dlg.setViewMode(QtGui.QFileDialog.Detail)
        dlg.selectFile(default_filename)
        dlg.setFilters(filters)

        if self.wildcard_index < filters.count():
            dlg.selectFilter(filters[self.wildcard_index])

        if self.action == 'open':
            dlg.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
            dlg.setFileMode(QtGui.QFileDialog.ExistingFile)
        else:
            dlg.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            dlg.setFileMode(QtGui.QFileDialog.AnyFile)

        return dlg

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _wildcard_default(self):
        """ Return the default wildcard. """

        return self.WILDCARD_ALL

#### EOF ######################################################################
