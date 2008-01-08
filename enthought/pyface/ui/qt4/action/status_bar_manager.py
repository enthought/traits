#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#------------------------------------------------------------------------------

# Major package imports.
from PyQt4 import QtGui

# Enthought library imports.
from enthought.traits.api import Any, HasTraits, List, Property, Str, Unicode


class StatusBarManager(HasTraits):
    """ A status bar manager realizes itself in a status bar control. """

    # FIXME v3: Is this used anywhere?
    # The manager's unique identifier (if it has one).
    id = Str

    # The message displayed in the first field of the status bar.
    message = Property

    # The messages to be displayed in the status bar fields.
    messages = List(Unicode)

    # The toolkit-specific control that represents the status bar.
    status_bar = Any
    
    ###########################################################################
    # 'StatusBarManager' interface.
    ###########################################################################
    
    def create_status_bar(self, parent):
        """ Creates a status bar. """

        if self.status_bar is None:
            self.status_bar = QtGui.QStatusBar(parent)
            self.status_bar.setSizeGripEnabled(False)

            if len(self.messages) > 1:
                self._show_messages()
            else:
                self.status_bar.showMessage(self.message)
            
        return self.status_bar

    ###########################################################################
    # Property handlers.
    ###########################################################################

    def _get_message(self):

        if len(self.messages) > 0:
            message = self.messages[0]
        else:
            message = ''

        return message

    def _set_message(self, value):

        if len(self.messages) > 0:
            old = self.messages[0]
            self.messages[0] = value
        else:
            old = ''
            self.messages.append(old)

        self.trait_property_changed('message', old, value)

    ###########################################################################
    # Trait event handlers.
    ###########################################################################

    def _messages_changed(self):
        """ Sets the text displayed on the status bar. """

        if self.status_bar is not None:
            self._show_messages()

    def _messages_items_changed(self):
        """ Sets the text displayed on the status bar. """

        if self.status_bar is not None:
            self._show_messages()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _show_messages(self):
        """ Display the list of messages. """

        # FIXME v3: At the moment we just string them together but we may
        # decide to put all but the first message into separate widgets.  We
        # probably also need to extend the API to allow a "message" to be a
        # widget - depends on what wx is capable of.
        self.status_bar.showMessage("  ".join(self.messages))

#### EOF ######################################################################
