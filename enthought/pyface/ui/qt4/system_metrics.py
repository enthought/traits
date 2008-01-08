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
from PyQt4 import QtGui

# Enthought library imports.
from enthought.traits.api import HasTraits, implements, Int, Property, Tuple

# Local imports.
from enthought.pyface.i_system_metrics import ISystemMetrics, MSystemMetrics


class SystemMetrics(MSystemMetrics, HasTraits):
    """ The toolkit specific implementation of a SystemMetrics.  See the
    ISystemMetrics interface for the API documentation.
    """

    implements(ISystemMetrics)

    #### 'ISystemMetrics' interface ###########################################

    screen_width = Property(Int)

    screen_height = Property(Int)

    dialog_background_color = Property(Tuple)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _get_screen_width(self):
        return QtGui.QApplication.instance().desktop().screenGeometry().width()

    def _get_screen_height(self):
        return QtGui.QApplication.instance().desktop().screenGeometry().height()

    def _get_dialog_background_color(self):
        color = QtGui.QApplication.instance().palette().color(QtGui.QPalette.Window)

        return (color.redF(), color.greenF(), color.blueF())


#### EOF ######################################################################
