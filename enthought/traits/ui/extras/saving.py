#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   06/18/2009
#
#------------------------------------------------------------------------------

""" Provides a lightweight framework that removes some of the drudge work
    involved with implementing user-friendly saving behavior in a Traits
    UI application.
"""

from __future__ import absolute_import

# ETS imports
from ....pyface.api import FileDialog, confirm, error, YES, CANCEL
from ....pyface.timer.api import Timer
from ...api import HasTraits, Str, Bool, Any, Int, Instance, on_trait_change
from ..api import Handler


class CanSaveMixin(HasTraits):
    """ A mixin-class for objects that wish to support GUI saving via a
        SaveHandler. It is the responsiblity of the child class to manage
        its dirty flag, which describes whether its information has changed
        since its last save.
    """

    filepath = Str
    dirty = Bool(False)

    #-----------------------------------------------------------------
    #  object interface
    #-----------------------------------------------------------------

    def __getstate__(self):
        """ We don't want to pickle the filepath because this can change,
            obviously, if the user moves around the pickled file.
        """
        state = super(CanSaveMixin, self).__getstate__()
        del state['filepath']
        del state['dirty']
        return state

    #-----------------------------------------------------------------
    #  CanSaveMixin interface
    #-----------------------------------------------------------------

    def validate(self):
        """ Returns whether the information in the object is valid to be saved
            in tuple form. The first item is the validation state (boolean) and
            the second item is the message to display if the object did not
            validate.

            By default, an object always validates.
        """
        return (True, '')

    def save(self):
        """ Saves the object to the path specified by its 'filepath' trait. This
            method should also reset the dirty flag on this object.
        """
        raise NotImplementedError


class SaveHandler(Handler):
    """ A Handler that facilates adding saving to a Traits UI application.
    """

    # The object which is to be saved (subclass of CanSaveMixin). It is assigned
    # to info.object in the 'init' method, which in many cases is what you want.
    # If not, override that method to set it to something else.
    saveObject = Any

    # The type of files to show in the save dialogs
    wildcard = Str('All files (*.*)|*.*')

    # The option extension which should appear at the end of all filenames. If
    # the user does not explicitly specifiy it, it is appended to the filename.
    extension = Str

    # This message to display when the Handler requests a save
    savePromptMessage = Str('Would you like to save?')

    # Whether to prompt for a save on exit if the save object is dirty
    promptOnExit = Bool(True)

    # Whether to allow the user to override a validation failure through a
    # confirmation dialog. By default, validation errors cannot be overriden.
    allowValidationBypass = Bool(False)

    # Whether to automatically save after a certain amount of time has passed
    # since the last save
    autosave = Bool(False)

    # Number of seconds between each autosave. Default is 5 minutes.
    autosaveInterval = Int(300)

    # If it is possible to override validation failures, this specifies whether
    # autosave will do so. If False and a validation errors occurs, no save
    # will occur.
    autosaveValidationBypass = Bool(True)

    # Protected traits
    _timer = Instance(Timer)

    #-----------------------------------------------------------------
    #  Handler interface
    #-----------------------------------------------------------------

    def init(self, info):
        """ Set the default save object (the object being handled). Also,
            perform a questionable hack by which we remove the handled
            object from the keybinding's controllers. This means that a
            keybinding to 'save' only calls this object, not the object
            being edited as well. (For reasons unclear, the KeyBinding handler
            API is radically different from the Action API, which is the reason
            that this problem exists. Keybindings are a UI concept--they should
            *not* call the model by default.)
        """
        keybindings = info.ui.key_bindings
        if keybindings is not None:
            keybindings.controllers.remove(info.object)

        self.saveObject = info.object
        return True

    def close(self, info, is_ok):
        """ Called when the user requests to close the interface. Returns a
            boolean indicating whether the window should be allowed to close.
        """
        if self.promptOnExit:
            return self.promptForSave(info)
        else:
            return True

    def closed(self, info, is_ok):
        """ Called after the window is destroyed. Makes sure that the autosave
            timer is stopped.
        """
        if self._timer:
            self._timer.Stop()

    #-----------------------------------------------------------------
    #  SaveHandler interface
    #-----------------------------------------------------------------

    def exit(self, info):
        """ Closes the UI unless a save prompt is cancelled. Provided for
            convenience to be used with a Menu action.
        """
        if self.close(info, True):
            info.ui.dispose()

    def save(self, info):
        """ Saves the object to its current filepath. If this is not specified,
            opens a dialog to select this path. Returns whether the save
            actually occured.
        """
        if self.saveObject.filepath == '':
            return self.saveAs(info)
        else:
            return self._validateAndSave()

    def saveAs(self, info):
        """ Saves the object to a new path, and sets this as the 'filepath' on
            the object. Returns whether the save actually occurred.
        """
        fileDialog = FileDialog(action='save as', title='Save As',
                                wildcard=self.wildcard,
                                parent=info.ui.control)
        fileDialog.open()
        if fileDialog.path == '' or fileDialog.return_code == CANCEL:
            return False
        else:
            extLen = len(self.extension)
            if extLen and fileDialog.path[-extLen-1:] != '.' + self.extension:
                fileDialog.path += '.' + self.extension
            self.saveObject.filepath = fileDialog.path
            return self._validateAndSave()

    def promptForSave(self, info, cancel=True):
        """ Prompts the user to save the object, if appropriate. Returns whether
            the user canceled the action that invoked this prompt.
        """
        if self.saveObject.dirty:
            code = confirm(info.ui.control, self.savePromptMessage,
                           title="Save now?", cancel=cancel)
            if code == CANCEL:
                return False
            elif code == YES:
                if not self.save(info):
                    return self.promptForSave(info, cancel)
        return True

    def _autosave(self):
        """ Called by the timer when an autosave should take place.
        """
        if self.saveObject.dirty and self.saveObject.filepath != '':
            success, message = self.saveObject.validate()
            if success or (self.allowValidationBypass and
                           self.autosaveValidationBypass):
                self.saveObject.save()

    @on_trait_change('autosave, autosaveInterval, saveObject')
    def _configure_timer(self):
        """ Creates, replaces, or destroys the autosave timer.
        """
        if self._timer:
            self._timer.Stop()
        if self.autosave and self.saveObject:
            self._timer = Timer(self.autosaveInterval * 1000, self._autosave)
        else:
            self._timer = None

    def _validateAndSave(self):
        """ Try to save to the current filepath. Returns whether whether the
            validation was successful/overridden (and the object saved).
        """
        success, message = self.saveObject.validate()
        if success:
            self.saveObject.save()
        else:
            title = "Validation error"
            if (self.allowValidationBypass and
                confirm(None, message, title=title) == YES):
                self.saveObject.save()
                success = True
            else:
                error(None, message, title=title)
        return success
