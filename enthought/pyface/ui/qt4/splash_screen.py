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
from logging import DEBUG

# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Any, Bool, Font, implements, Instance, Int
from enthought.traits.api import Tuple, Unicode

# Local imports.
from enthought.pyface.i_splash_screen import ISplashScreen, MSplashScreen
from enthought.pyface.image_resource import ImageResource
from window import Window


class SplashScreen(MSplashScreen, Window):
    """ The toolkit specific implementation of a SplashScreen.  See the
    ISplashScreen interface for the API documentation.
    """

    implements(ISplashScreen)

    #### 'ISplashScreen' interface ############################################

    image = Instance(ImageResource, ImageResource('splash'))

    log_level = Int(DEBUG)

    show_log_messages = Bool(True)

    text = Unicode

    text_color = Any

    text_font = Any

    text_location  = Tuple(5, 5)

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        splash_screen = QtGui.QSplashScreen(self.image.create_image())
        self._qt4_show_message(splash_screen)

        return splash_screen

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _text_changed(self):
        """ Called when the splash screen text has been changed. """

        if self.control is not None:
            self._qt4_show_message(self.control)

    def _qt4_show_message(self, control):
        """ Set the message text for a splash screen control. """

        if self.text_font is not None:
            control.setFont(self.text_font)

        if self.text_color is None:
            text_color = QtCore.Qt.black
        else:
            # Until we get the type of this trait finalised (ie. when TraitsUI
            # supports PyQt) convert it explcitly to a colour.
            text_color = QtGui.QColor(self.text_color)

        control.showMessage(self.text, QtCore.Qt.AlignLeft, text_color)

#### EOF ######################################################################
