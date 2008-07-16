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

import logging

# Enthought library imports.
from enthought.logger.agent.quality_agent_view import QualityAgentView
from enthought.logger.widget.logger_widget import LoggerWidget
from enthought.traits.api import Any, Str

from enthought.pyface.workbench.api import View


class LoggerView(View):
    """ The Workbench View showing the list of log items.
    """

    id = Str('enthought.logger.plugin.view.logger_view.LoggerView')
    name = Str('Logger')

    # The LoggerService we are associated with.
    service = Any()

    widget = Any()
    
    ###########################################################################
    # 'View' interface.
    ###########################################################################
    def create_control(self, parent):
        """ Creates the toolkit-specific control that represents the view.
        'parent' is the toolkit-specific control that is the view's parent.
        """
        logging.info('LoggerView.create_control()')

        # create the widget
        self.widget = LoggerWidget(parent, self.service)

        # set the double click action
        if self.service.preferences.enable_agent:
            self.widget.set_selection_action(QualityAgentView)

        # Do one initial refresh in order to display items that were logged
        # before the widget started up.
        self.service.refresh_view()

        logging.info('  self.widget = %r', self.widget)
        return self.widget

####EOF##################################################################

