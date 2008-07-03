#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" A page in a wizard. """


# Major package imports.
from PyQt4 import QtGui

# Enthought library imports.
from enthought.traits.api import Bool, implements, HasTraits, Str, Unicode
from enthought.pyface.wizard.i_wizard_page import IWizardPage, MWizardPage


class WizardPage(MWizardPage, HasTraits):
    """ The toolkit specific implementation of a WizardPage.

    See the IWizardPage interface for the API documentation.

    """

    implements(IWizardPage)

    #### 'IWizardPage' interface ##############################################

    id = Str

    complete = Bool(False)

    heading = Unicode

    subheading = Unicode

    ###########################################################################
    # 'IWizardPage' interface.
    ###########################################################################

    def create_page(self, parent):
        """ Creates the wizard page. """

        # This indirection is to maintain compatibility with the wx version.
        return self._create_page_content(parent)

    ###########################################################################
    # Protected 'IWizardPage' interface.
    ###########################################################################

    def _create_page_content(self, parent):
        """ Creates the actual page content. """

        # Dummy implementation - override! 
        control = QtGui.QWidget(parent)

        palette = control.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('yellow'))
        control.setPalette(palette)
        control.setAutoFillBackground(True)

        return control

#### EOF ######################################################################
