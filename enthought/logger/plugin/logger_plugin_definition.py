#------------------------------------------------------------------------------
# Copyright (c) 2005-2006, Enthought, Inc.
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
""" Logger Plugin. """


# Enthought library imports.
from enthought.envisage import PluginDefinition, get_using_workbench

# Are we using the old UI plugin, or the shiny new Workbench plugin?
USING_WORKBENCH = get_using_workbench()

# Plugin definition imports.
from enthought.envisage.core.core_plugin_definition \
     import PluginDefinition, Preferences

if USING_WORKBENCH:
    from enthought.envisage.workbench.preference.preference_plugin_definition \
         import PreferencePages, Page
    from enthought.envisage.workbench.workbench_plugin_definition import \
         View, Workbench    
else:
    from enthought.envisage.ui.preference.preference_plugin_definition \
         import PreferencePages, Page
    from enthought.envisage.ui.ui_plugin_definition \
         import UIViews, View


# The plugin's globally unique identifier (also used as the prefix for all
# identifiers defined in this module).
ID = "enthought.logger"


###############################################################################
# Extensions.
###############################################################################

#### Preferences ##############################################################

preferences = Preferences(
    defaults = {
        'log_level' : 'Debug',
        'smtp_server' : 'mailhost.conocophillips.net',
        'to_address' : 'proava2-dev@enthought.com',
        'from_address' : '',
        'enable_agent' : False
    }
)

#### Preference pages #########################################################

preference_pages = PreferencePages(
    pages = [
        Page(
            id         = ID + "LoggerPreferencePage",
            class_name = ID + ".plugin.view.logger_preference_page.LoggerPreferencePage",
            name       = "Logger",
            category   = "",
        )
    ]
)

#### Views ####################################################################
if USING_WORKBENCH:
    ui_views = Workbench(
        views = [
            View(
                id         = ID + ".plugin.view.logger_view.LoggerView",
                class_name = ID + ".plugin.view.logger_view.LoggerView",
                image      = "images/logger.png",
                name       = "Logger",
                position   = "bottom",
            ),
        ]
    )
    requires = ["enthought.envisage.workbench"]

else:
    ui_views = UIViews(
        views = [
            View(
                id         = ID + ".plugin.view.logger_view.LoggerView",
                class_name = ID + ".plugin.view.logger_view.LoggerView",
                image      = "images/logger.png",
                name       = "Logger",
                position   = "bottom",
            ),
        ]
    )
    requires = ["enthought.envisage.ui"]

###############################################################################
# The plugin definition.
###############################################################################

PluginDefinition(
    # The plugin's globally unique identifier.
    id = ID,

    # The name of the class that implements the plugin.
    class_name = ID + ".plugin.logger_plugin.LoggerPlugin",

    # General information about the plugin.
    name          = "Application Logger Plugin",
    version       = "1.0.0",
    provider_name = "Enthought Inc",
    provider_url  = "www.enthought.com",
    enabled       = True,
    autostart     = False,
    
    # The Id's of the plugins that this plugin requires.
    requires = requires,

    # The contributions that this plugin makes to extension points offered by
    # either itself or other plugins.
    extensions = [ui_views, preferences, preference_pages]
)

#### EOF ######################################################################
