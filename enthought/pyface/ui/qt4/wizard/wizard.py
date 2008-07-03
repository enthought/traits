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
""" The base class for all pyface wizards. """


# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, implements, Instance, Unicode
from enthought.pyface.api import Dialog
from enthought.pyface.wizard.i_wizard import IWizard, MWizard
from enthought.pyface.wizard.wizard_controller import WizardController


class Wizard(MWizard, Dialog):
    """ The base class for all pyface wizards.

    See the IWizard interface for the API documentation.

    """

    implements(IWizard)

    #### 'IWizard' interface ##################################################

    controller = Instance(WizardController)

    show_cancel = Bool(True)

    #### 'IWindow' interface ##################################################

    title = Unicode('Wizard')

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        pass

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        control = _Wizard(parent, self.controller)

        control.setWindowTitle(self.title)
        control.setModal(self.style == 'modal')

        if not self.show_cancel:
            control.setOption(QtGui.QWizard.NoCancelButton)

        if self.help_id:
            control.setOption(QtGui.QWizard.HaveHelpButton)
            QtCore.QObject.connect(control, QtCore.SIGNAL('helpRequested()'),
                    self._help_requested)

        # Add the pages.
        for page in self.pages:
            control.addWizardPage(page)

        # Set the start page.
        control.setStartWizardPage()

        return control

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _help_requested(self):
        """ Called when the 'Help' button is pressed. """

        # FIXME: Hook into a help system.
        print "Show help for", self.help_id


class _Wizard(QtGui.QWizard):
    """ A QWizard sub-class that hooks into the controller to determine the
    next page to show. """

    def __init__(self, parent, controller):
        """ Initialise the object. """

        QtGui.QWizard.__init__(self, parent)

        self._controller = controller
        self._ids = {}

    def addWizardPage(self, page):
        """ Add a page that implements IWizardPage. """

        # We must pass a parent otherwise TraitsUI does the wrong thing.
        qpage = page.create_page(self)

        # We allow some flexibility with the sort of control we are given.
        if not isinstance(qpage, QtGui.QWizardPage):
            wp = _WizardPage(page)

            if isinstance(qpage, QtGui.QLayout):
                wp.setLayout(qpage)
            else:
                assert isinstance(qpage, QtGui.QWidget)

                lay = QtGui.QVBoxLayout()
                lay.addWidget(qpage)

                wp.setLayout(lay)

            qpage = wp

        qpage.setTitle(page.heading)
        qpage.setSubTitle(page.subheading)

        id = self.addPage(qpage)
        self._ids[id] = page

    def setStartWizardPage(self):
        """ Set the first page. """

        page = self._controller.get_first_page()
        id = self._page_to_id(page)

        if id >= 0:
            self.setStartId(id)

    def nextId(self):
        """ Reimplemented to return the id of the next page to display. """

        current = self._ids[self.currentId()]
        next = self._controller.get_next_page(current)

        return self._page_to_id(next)

    def _page_to_id(self, page):
        """ Return the id of the given page. """

        if page is None:
            id = -1
        else:
            for id, p in self._ids.items():
                if p is page:
                    break
            else:
                id = -1

        return id


class _WizardPage(QtGui.QWizardPage):
    """ A QWizardPage sub-class that hooks into the IWizardPage's 'complete'
    trait. """

    def __init__(self, page):
        """ Initialise the object. """

        QtGui.QWizardPage.__init__(self)

        page.on_trait_change(self._on_complete_changed, 'complete')

        self._page = page

    def isComplete(self):
        """ Reimplemented to return the state of the 'complete' trait. """

        return self._page.complete

    def _on_complete_changed(self):
        """ The trait handler for when the page's completion state changes. """

        self.emit(QtCore.SIGNAL('completeChanged()'))

#### EOF ######################################################################
