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
from enthought.resource.api import ResourceFactory


class PyfaceResourceFactory(ResourceFactory):
    """ The implementation of a shared resource manager. """

    ###########################################################################
    # 'ResourceFactory' interface.
    ###########################################################################

    def image_from_file(self, filename):
        """ Creates an image from the data in the specified filename. """

        return QtGui.QPixmap(filename)

    def image_from_data(self, data):
        """ Creates an image from the specified data. """

        image = QtGui.QPixmap()
        image.loadFromData(data)

        return image

#### EOF ######################################################################
