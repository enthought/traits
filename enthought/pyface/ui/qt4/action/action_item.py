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
""" The PyQt specific implementations the action manager internal classes. """


# Standard libary imports.
from inspect import getargspec

# Major package imports.
from PyQt4 import QtGui

# Enthought library imports.
from enthought.traits.api import Any, Bool, HasTraits

# Local imports.
from enthought.pyface.action.action_event import ActionEvent


class _MenuItem(HasTraits):
    """ A menu item representation of an action item. """

    #### '_MenuItem' interface ################################################
    
    # Is the item checked?
    checked = Bool(False)

    # A controller object we delegate taking actions through (if any).
    controller = Any
    
    # Is the item enabled?
    enabled = Bool(True)
    
    # Is the item visible?
    visible = Bool(True)
    
    # The radio group we are part of (None if the menu item is not part of such
    # a group).
    group = Any
    
    ###########################################################################
    # 'object' interface.
    ###########################################################################
    
    def __init__(self, parent, menu, item, controller):
        """ Creates a new menu item for an action item. """

        self.item = item
        action = item.action

        # FIXME v3: This is a wx'ism and should be hidden in the toolkit code.
        self.control_id = None

        if action.image is None:
            self.control = menu.addAction(action.name, self._qt4_on_triggered,
                    action.accelerator)
        else:
            self.control = menu.addAction(action.image.create_icon(),
                    action.name, self._qt4_on_triggered, action.accelerator)

        self.control.setToolTip(action.tooltip)
        self.control.setWhatsThis(action.description)
        self.control.setEnabled(action.enabled)
        self.control.setVisible(action.visible)

        if action.style == 'toggle':
            self.control.setCheckable(True)
            self.control.setChecked(action.checked)
        elif action.style == 'radio':
            # Create an action group if it hasn't already been done.
            try:
                ag = item.parent._qt4_ag
            except AttributeError:
                ag = item.parent._qt4_ag = QtGui.QActionGroup(parent)

            self.control.setActionGroup(ag)

            self.control.setCheckable(True)
            self.control.setChecked(action.checked)

        # Listen for trait changes on the action (so that we can update its
        # enabled/disabled/checked state etc).
        action.on_trait_change(self._on_action_enabled_changed, 'enabled')
        action.on_trait_change(self._on_action_visible_changed, 'visible')
        action.on_trait_change(self._on_action_checked_changed, 'checked')
        action.on_trait_change(self._on_action_name_changed, 'name')

        if controller is not None:
            self.controller = controller
            controller.add_to_menu(self)
    
    ###########################################################################
    # Private interface. 
    ###########################################################################

    def _qt4_on_triggered(self):
        """ Called when the menu item has been clicked. """

        action = self.item.action
        action_event = ActionEvent()
        
        is_checkable = action.style in ['radio', 'toggle']
        
        # Perform the action!
        if self.controller is not None:
            if is_checkable:
                # fixme: There is a difference here between having a controller
                # and not in that in this case we do not set the checked state
                # of the action! This is confusing if you start off without a
                # controller and then set one as the action now behaves
                # differently!
                self.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it. This is also
            # useful as Traits UI controllers *never* require the event.
            args, varargs, varkw, dflts = getargspec(self.controller.perform)

            # If the only arguments are 'self' and 'action' then don't pass
            # the event!
            if len(args) == 2:
                self.controller.perform(action)
            
            else:
                self.controller.perform(action, action_event)
            
        else:
            if is_checkable:
                action.checked = self.control.isChecked()
                
            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it.
            args, varargs, varkw, dflts = getargspec(action.perform)

            # If the only argument is 'self' then don't pass the event!
            if len(args) == 1:
                action.perform()
            
            else:
                action.perform(action_event)

    #### Trait event handlers #################################################

    def _enabled_changed(self):
        """ Called when our 'enabled' trait is changed. """

        self.control.setEnabled(self.enabled)

    def _visible_changed(self):
        """ Called when our 'visible' trait is changed. """

        self.control.setVisible(self.visible)

    def _checked_changed(self):
        """ Called when our 'checked' trait is changed. """

        self.control.setChecked(self.checked)

    def _on_action_enabled_changed(self, action, trait_name, old, new):
        """ Called when the enabled trait is changed on an action. """

        self.control.setEnabled(action.enabled)

    def _on_action_visible_changed(self, action, trait_name, old, new):
        """ Called when the visible trait is changed on an action. """

        self.control.setVisible(action.visible)

    def _on_action_checked_changed(self, action, trait_name, old, new):
        """ Called when the checked trait is changed on an action. """

        self.control.setChecked(action.checked)

    def _on_action_name_changed(self, action, trait_name, old, new):
        """ Called when the name trait is changed on an action. """

        self.control.setText(action.name)


class _Tool(HasTraits):
    """ A tool bar tool representation of an action item. """

    #### '_Tool' interface ####################################################
    
    # Is the item checked?
    checked = Bool(False)

    # A controller object we delegate taking actions through (if any).
    controller = Any

    # Is the item enabled?
    enabled = Bool(True)

    # Is the item visible?
    visible = Bool(True)

    # The radio group we are part of (None if the tool is not part of such a
    # group).
    group = Any

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, parent, tool_bar, image_cache, item, controller,
                 show_labels):
        """ Creates a new tool bar tool for an action item. """

        self.item = item
        self.tool_bar = tool_bar
        action = item.action

        # FIXME v3: This is a wx'ism and should be hidden in the toolkit code.
        self.control_id = None

        if action.image is None:
            self.control = tool_bar.addAction(action.name,
                    self._qt4_on_triggered)
        else:
            self.control = tool_bar.addAction(action.image.create_icon(),
                    action.name, self._qt4_on_triggered)

        self.control.setToolTip(action.tooltip)
        self.control.setWhatsThis(action.description)
        self.control.setEnabled(action.enabled)
        self.control.setVisible(action.visible)

        if action.style == 'toggle':
            self.control.setCheckable(True)
            self.control.setChecked(action.checked)
        elif action.style == 'radio':
            # Create an action group if it hasn't already been done.
            try:
                ag = item.parent._qt4_ag
            except AttributeError:
                ag = item.parent._qt4_ag = QtGui.QActionGroup(parent)

            self.control.setActionGroup(ag)

            self.control.setCheckable(True)
            self.control.setChecked(action.checked)

        # Keep a reference in the action.  This is done to make sure we live as
        # long as the action (and still respond to its signals) and don't die
        # if the manager that created us is garbage collected.
        self.control._tool_instance = self

        # Listen for trait changes on the action (so that we can update its
        # enabled/disabled/checked state etc).
        action.on_trait_change(self._on_action_enabled_changed, 'enabled')
        action.on_trait_change(self._on_action_visible_changed, 'visible')
        action.on_trait_change(self._on_action_checked_changed, 'checked')

        if controller is not None:
            self.controller = controller
            controller.add_to_toolbar(self)

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _qt4_on_triggered(self):
        """ Called when the tool bar tool is clicked. """

        action = self.item.action
        action_event = ActionEvent()

        # Perform the action!
        if self.controller is not None:
            # fixme: There is a difference here between having a controller
            # and not in that in this case we do not set the checked state
            # of the action! This is confusing if you start off without a
            # controller and then set one as the action now behaves
            # differently!
            self.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it. This is also
            # useful as Traits UI controllers *never* require the event.
            args, varargs, varkw, dflts = getargspec(self.controller.perform)

            # If the only arguments are 'self' and 'action' then don't pass
            # the event!
            if len(args) == 2:
                self.controller.perform(action)
            
            else:
                self.controller.perform(action, action_event)
            
        else:
            action.checked = self.control.isChecked()

            # Most of the time, action's do no care about the event (it
            # contains information about the time the event occurred etc), so
            # we only pass it if the perform method requires it.
            args, varargs, varkw, dflts = getargspec(action.perform)

            # If the only argument is 'self' then don't pass the event!
            if len(args) == 1:
                action.perform()
            
            else:
                action.perform(action_event)

    #### Trait event handlers #################################################

    def _enabled_changed(self):
        """ Called when our 'enabled' trait is changed. """

        self.control.setEnabled(self.enabled)
    
    def _visible_changed(self):
        """ Called when our 'visible' trait is changed. """

        self.control.setVisible(self.visible)
    
    def _checked_changed(self):
        """ Called when our 'checked' trait is changed. """

        self.control.setChecked(self.checked)

    def _on_action_enabled_changed(self, action, trait_name, old, new):
        """ Called when the enabled trait is changed on an action. """

        self.control.setEnabled(action.enabled)
    
    def _on_action_visible_changed(self, action, trait_name, old, new):
        """ Called when the visible trait is changed on an action. """

        self.control.setVisible(action.visible)
    
    def _on_action_checked_changed(self, action, trait_name, old, new):
        """ Called when the checked trait is changed on an action. """

        self.control.setChecked(action.checked)


class _PaletteTool(HasTraits):
    """ A tool palette representation of an action item. """

    #### '_PaletteTool' interface #############################################

    # The radio group we are part of (None if the tool is not part of such a
    # group).
    group = Any

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, tool_palette, image_cache, item, show_labels):
        """ Creates a new tool palette tool for an action item. """

        self.item = item
        self.tool_palette = tool_palette

        action = self.item.action
        label = action.name

        # Tool palette tools never have '...' at the end.
        if label.endswith('...'):
            label = label[:-3]

        # And they never contain shortcuts.
        label = label.replace('&', '')

        image = action.image.create_image()
        path = action.image.absolute_path
        bmp = image_cache.get_bitmap(path)

        kind    = action.style
        tooltip = action.tooltip
        longtip = action.description

        if not show_labels:
            label = ''

        # Add the tool to the tool palette.
        self.tool_id = tool_palette.add_tool(label, bmp, kind, tooltip,longtip)
        tool_palette.toggle_tool(self.tool_id, action.checked)
        tool_palette.enable_tool(self.tool_id, action.enabled)
        tool_palette.on_tool_event(self.tool_id, self._on_tool)

        # Listen to the trait changes on the action (so that we can update its
        # enabled/disabled/checked state etc).
        action.on_trait_change(self._on_action_enabled_changed, 'enabled')
        action.on_trait_change(self._on_action_checked_changed, 'checked')

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait event handlers #################################################

    def _on_action_enabled_changed(self, action, trait_name, old, new):
        """ Called when the enabled trait is changed on an action. """

        self.tool_palette.enable_tool(self.tool_id, action.enabled)

        return

    def _on_action_checked_changed(self, action, trait_name, old, new):
        """ Called when the checked trait is changed on an action. """

        if action.style == 'radio':
            # If we're turning this one on, then we need to turn all the others
            # off.  But if we're turning this one off, don't worry about the
            # others.
            if new:
                for item in self.item.parent.items:
                    if item is not self.item:
                        item.action.checked = False

        # This will *not* emit a tool event.
        self.tool_palette.toggle_tool(self.tool_id, new)

        return

    #### Tool palette event handlers ##########################################

    def _on_tool(self, event):
        """ Called when the tool palette button is clicked. """

        action = self.item.action
        action_event = ActionEvent()

        is_checkable = (action.style == 'radio' or action.style == 'check')

        # Perform the action!
        action.checked = self.tool_palette.get_tool_state(self.tool_id) == 1
        action.perform(action_event)

        return

#### EOF ######################################################################
