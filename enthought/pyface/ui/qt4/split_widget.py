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
""" Mix-in class for split widgets. """


# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Callable, Enum, Float, HasTraits, implements

# Local imports.
from enthought.pyface.i_split_widget import ISplitWidget, MSplitWidget


class SplitWidget(MSplitWidget, HasTraits):
    """ The toolkit specific implementation of a SplitWidget.  See the
    ISPlitWidget interface for the API documentation.
    """

    implements(ISplitWidget)

    #### 'ISplitWidget' interface #############################################

    direction = Enum('vertical', 'vertical', 'horizontal')

    ratio = Float(0.5)

    lhs = Callable

    rhs = Callable

    ###########################################################################
    # Protected 'ISplitWidget' interface.
    ###########################################################################

    def _create_splitter(self, parent):
        """ Create the toolkit-specific control that represents the widget. """

        splitter = QtGui.QSplitter(parent)

        # Yes, this is correct.
        if self.direction == 'horizontal':
            splitter.setOrientation(QtCore.Qt.Vertical)

        # Only because the wx implementation does the same.
        splitter.setChildrenCollapsible(False)

        # Left hand side/top.
        splitter.addWidget(self._create_lhs(splitter))

        # Right hand side/bottom.
        splitter.addWidget(self._create_rhs(splitter))

        # Set the initial splitter position.
        if self.direction == 'horizontal':
            pos = splitter.sizeHint().height()
        else:
            pos = splitter.sizeHint().width()

        splitter.setSizes([int(pos * self.ratio), int(pos * (1.0 - self.ratio))])

        return splitter

    def _create_lhs(self, parent):
        """ Creates the left hand/top panel depending on the direction. """

        if self.lhs is not None:
            lhs = self.lhs(parent)
            if not isinstance(lhs, QtGui.QWidget):
                lhs = lhs.control
                
        else:
            # Dummy implementation - override!
            lhs = QtGui.QWidget(parent)

        return lhs

    def _create_rhs(self, parent):
        """ Creates the right hand/bottom panel depending on the direction. """

        if self.rhs is not None:
            rhs = self.rhs(parent)
            if not isinstance(rhs, QtGui.QWidget):
                rhs = rhs.control
        
        else:
            # Dummy implementation - override!
            rhs = QtGui.QWidget(parent)

        return rhs

#### EOF ######################################################################
