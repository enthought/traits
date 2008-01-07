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
from enthought.logger.agent.quality_agent_view import QualityAgentView
from enthought.logger.plugin.logger_plugin import LoggerPlugin
from enthought.logger.widget.logger_widget import LoggerWidget

# Are we using the old UI plugin, or the shiny new Workbench plugin?
USING_WORKBENCH = get_using_workbench()

# Conditional imports.
if USING_WORKBENCH:
    from enthought.envisage.workbench import View
else:
    from enthought.envisage.ui import View


class LoggerView(View):
    
    widget = None
    
    ###########################################################################
    # 'View' interface.
    ###########################################################################
    def _create_contents(self, parent):
        """ Creates the toolkit-specific control that represents the view.
        'parent' is the toolkit-specific control that is the view's parent.
        """

        # register the view with the plugin
        LoggerPlugin.instance.plugin_view = self
        
        # create the widget
        self.widget = LoggerWidget(parent)

        # set the double click action
        enable_agent = LoggerPlugin.instance.preferences.get('enable_agent')
        if enable_agent == True:
            self.widget.set_selection_action(QualityAgentView)

        return self.widget

    create_control = _create_contents

####EOF##################################################################

