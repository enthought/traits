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
#  'PyMimeData' class:
#-------------------------------------------------------------------------------

class PyMimeData(QtCore.QMimeData):
    """ The PyMimeData wraps a Python instance as MIME data.
    """
    # The MIME type for instances.
    MIME_TYPE = QtCore.QString('application/x-ets-qt4-instance')

    def __init__(self, data=None):
        """ Initialise the instance.
        """
        QtCore.QMimeData.__init__(self)

        # Keep a local reference to be returned if possible.
        self._local_instance = data

        if data is not None:
            # We may not be able to pickle the data.
            try:
                pdata = dumps(data)
            except:
                return

            # This format (as opposed to using a single sequence) allows the
            # type to be extracted without unpickling the data itself.
            self.setData(self.MIME_TYPE, dumps(data.__class__) + pdata)

    @classmethod
    def coerce(cls, md):
        """ Coerce a QMimeData instance to a PyMimeData instance if possible.
        """
        # See if the data is already of the right type.  If it is then we know
        # we are in the same process.
        if isinstance(md, cls):
            return md

        # See if the data type is supported.
        if not md.hasFormat(cls.MIME_TYPE):
            return None

        nmd = cls()
        nmd.setData(cls.MIME_TYPE, md.data())

        return nmd

    def instance(self):
        """ Return the instance.
        """
        if self._local_instance is not None:
            return self._local_instance

        io = StringIO(str(self.data(self.MIME_TYPE)))

        try:
            # Skip the type.
            load(io)

            # Recreate the instance.
            return load(io)
        except:
            pass

        return None

    def instanceType(self):
        """ Return the type of the instance.
        """
        if self._local_instance is not None:
            return self._local_instance.__class__

        try:
            return loads(str(self.data(self.MIME_TYPE)))
        except:
            pass

        return None

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
    #  Instance property methods:
    #---------------------------------------------------------------------------
           
    def _get_instance(self):
        """ The instance getter.
        """
        md = PyMimeData.coerce(self.clipboard.mimeData())
        if md is None:
            return None

        return md.instance()

    def _set_instance(self, data):
        """ The instance setter.
        """
        self.clipboard.setMimeData(PyMimeData(data))

    def _get_has_instance(self):
        """ The has_instance getter.
        """
        return self.clipboard.mimeData().hasFormat(PyMimeData.MIME_TYPE)

    def _get_instance_type(self):
        """ The instance_type getter.
        """
        md = PyMimeData.coerce(self.clipboard.mimeData())
        if md is None:
            return None

        return md.instanceType()

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
