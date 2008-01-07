#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought logger package component>
#------------------------------------------------------------------------------

# Enthought library imports.
from enthought.envisage import get_using_workbench
from enthought.logger.plugin.logger_plugin import LoggerPlugin

# Are we using the old UI plugin, or the shiny new Workbench plugin?
USING_WORKBENCH = get_using_workbench()

if USING_WORKBENCH:
    from enthought.envisage.workbench.preference import WorkbenchPreferencePage
else:
    from enthought.envisage.ui.preference import WorkbenchPreferencePage


class LoggerPreferencePage(WorkbenchPreferencePage):
    """ A preference page for the logger plugin. """


    ###########################################################################
    # Protected 'WorkbenchPreferencePage' interface.
    ###########################################################################

    def create_control(self, parent):
        """ Creates the toolkit-specific control for the page. """

        # Initialize the page with the preferences.
        WorkbenchPreferencePage._initialize_preferences(self)

        # The control is just the page's trait sheet!
        ui = LoggerPlugin.instance.edit_traits(view='view', parent=parent, 
                                               kind='subpanel')

        return ui.control

    def restore_defaults(self):
        super(LoggerPreferencePage, self).restore_defaults()
        
        # update the properties so the view gets updated
        level = LoggerPlugin.instance.preferences.get('log_level')
        LoggerPlugin.instance.level = level

        enable_agent = LoggerPlugin.instance.preferences.get('enable_agent')
        LoggerPlugin.instance.enable_agent = enable_agent
        
        smtp_server = LoggerPlugin.instance.preferences.get('smtp_server')
        LoggerPlugin.instance.smtp_server = smtp_server

        to_address = LoggerPlugin.instance.preferences.get('to_address')
        LoggerPlugin.instance.to_address = to_address

        from_address = LoggerPlugin.instance.preferences.get('from_address')
        LoggerPlugin.instance.from_address = from_address

    def _get_preferences(self):
        """ Returns the preferences that this page is editing. """
        
        return LoggerPlugin.instance.preferences
        
#### EOF ######################################################################
