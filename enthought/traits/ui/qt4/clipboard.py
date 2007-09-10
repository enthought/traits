#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Implements a wrapper around the PyQt clipboard that handles Python objects
using pickle.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle import dumps, load, loads

from cStringIO import StringIO

from PyQt4 import QtCore, QtGui

from enthought.traits.api import HasTraits, Instance, Property

#-------------------------------------------------------------------------------
#  '_Clipboard' class:
#-------------------------------------------------------------------------------
                               
class _Clipboard(HasTraits):
    """ The _Clipboard class provides a wrapper around the PyQt clipboard.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The instance on the clipboard (if any).
    instance = Property

    # Set if the clipboard contains an instance.
    has_instance = Property
           
    # The type of the instance on the clipboard (if any).
    instance_type = Property

    # The application clipboard.
    clipboard = Instance(QtGui.QClipboard)

    #---------------------------------------------------------------------------
    #  Non-trait class attributes:
    #---------------------------------------------------------------------------

    # The private MIME type for instances.
    _MT_INSTANCE = QtCore.QString('application/x-ets-qt4-instance')

    #---------------------------------------------------------------------------
    #  Instance property methods:
    #---------------------------------------------------------------------------
           
    def _get_instance(self):
        """ The instance getter.
        """
        md = self.clipboard.mimeData()
        if md is None:
            return None

        ba = md.data(self._MT_INSTANCE)
        if ba.isEmpty():
            return None

        io = StringIO(str(ba))

        # Skip the instance type.
        load(io)

        return load(io)

    def _set_instance(self, data):
        """ The instance setter.
        """
        md = QtCore.QMimeData()

        # This format (as opposed to using a sequence) allows the type to be
        # extracted without unpickling the data itself.
        md.setData(self._MT_INSTANCE, dumps(data.__class__) + dumps(data))

        self.clipboard.setMimeData(md)

    def _get_has_instance(self):
        """ The has_instance getter.
        """
        md = self.clipboard.mimeData()
        if md is None:
            return None

        return md.hasFormat(self._MT_INSTANCE)

    def _get_instance_type(self):
        """ The instance_type getter.
        """
        md = self.clipboard.mimeData()
        if md is None:
            return None

        ba = md.data(self._MT_INSTANCE)
        if ba.isEmpty():
            return None

        return loads(str(ba))

    #---------------------------------------------------------------------------
    #  Other trait handlers:
    #---------------------------------------------------------------------------

    def _clipboard_default(self):
        """ Initialise the clipboard.
        """
        return QtGui.QApplication.clipboard()

#-------------------------------------------------------------------------------
#  The singleton clipboard instance.
#-------------------------------------------------------------------------------
                               
clipboard = _Clipboard()
