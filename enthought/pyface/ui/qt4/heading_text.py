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
from enthought.traits.api import implements, Instance, Int, Unicode

# Local imports.
from enthought.pyface.i_heading_text import IHeadingText, MHeadingText
from enthought.pyface.image_resource import ImageResource
from widget import Widget


class HeadingText(MHeadingText, Widget):
    """ The toolkit specific implementation of a HeadingText.  See the
    IHeadingText interface for the API documentation.
    """

    implements(IHeadingText)

    #### 'IHeadingText' interface #############################################
    
    level = Int(1)

    text = Unicode('Default')
    
    image = Instance(ImageResource, ImageResource('heading_level_1'))

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, parent, **traits):
        """ Creates the panel. """

        # Base class constructor.
        super(HeadingText, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_control(self, parent):
        """ Create the toolkit-specific control that represents the widget. """

        label = QtGui.QLabel(self.text, parent)

        label.setFrameShape(QtGui.QFrame.Box)
        label.setFrameShadow(QtGui.QFrame.Plain)

        brush = QtGui.QBrush(self.image.create_image())
        pal = QtGui.QPalette(label.palette())
        pal.setBrush(QtGui.QPalette.Window, brush)
        label.setPalette(pal)
        label.setAutoFillBackground(True)

        return label

    #### Trait event handlers #################################################

    def _text_changed(self, new):
        """ Called when the text is changed. """

        if self.control is not None:
            self.control.setText(new)

#### EOF ######################################################################
