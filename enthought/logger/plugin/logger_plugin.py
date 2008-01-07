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
""" Logger plugin. """

# Standard library imports.
import logging

# Enthought library imports.
from enthought.envisage import Plugin
from enthought.logger.log_queue_handler import log_queue_handler
from enthought.logger.plugin.services import ILOGGER
from enthought.traits.api import Bool, Str, Trait, Undefined
from enthought.traits.ui.api import View, Group, Item, EnumEditor


class LoggerPlugin(Plugin):
    """ Logger plugin. """

    # The shared plugin instance.
    instance = None
    
    # The handler we use
    handler = None

    # The view we use
    plugin_view = None
    
    # The log levels
    level = Trait( 'Info', {'Debug'    : logging.DEBUG,
                            'Info'     : logging.INFO,
                            'Warning'  : logging.WARNING,
                            'Error'    : logging.ERROR,
                            'Critical' : logging.CRITICAL} )

    enable_agent = Bool(False)
    smtp_server = Str
    to_address = Str
    from_address = Str
    
    # The view used to change the plugin preferences
    view = View(Group(Group(Item(name='level',
                                 editor=EnumEditor(values={
                                    'Debug'    : '1:Debug',
                                    'Info'     : '2:Info',
                                    'Warning'  : '3:Warning',
                                    'Error'    : '4:Error' ,
                                    'Critical' : '5:Critical'})), 
                            label='Logger Settings', show_border=True),
                      Group(Item(name='10')),
                      Group(Group(
                            Group(Item(name='enable_agent', label='Enable quality agent'), show_left=False),
                            Group(Item(name='smtp_server', label='SMTP server'),
                                  Item(name='from_address'), 
                                  Item(name='to_address'), enabled_when='enable_agent==True')),
                            label='Quality Agent Settings', show_border=True)
                     )
               )

        
    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, **kw):
        """ Creates a new plugin. """

        # Base-class constructor.
        super(LoggerPlugin, self).__init__(**kw)
        
        # Set the shared instance.
        LoggerPlugin.instance = self
        
        return


    def _level_changed(self, old, new):
        if(new != None and new != Undefined and self.handler != None):
            self.handler.setLevel(self.level_)
            self.preferences.set('log_level', self.level)            
        return

            
    def _enable_agent_changed(self, old, new):
        if(new != None and new != Undefined):
            self.preferences.set('enable_agent', self.enable_agent)
        if(new):
            if(self.plugin_view != None):
                from enthought.logger.agent.quality_agent_view import QualityAgentView
                self.plugin_view.widget.set_selection_action(QualityAgentView)
        else:
            if(self.plugin_view != None):
                from enthought.logger.plugin.view.log_detail_view import LogDetailView
                self.plugin_view.widget.set_selection_action(LogDetailView)
            
        return
        
            
    def _smtp_server_changed(self, old, new):
        if(new != None and new != Undefined):
            self.preferences.set('smtp_server', self.smtp_server)
        return
        
            
    def _from_address_changed(self, old, new):
        if(new != None and new != Undefined):
            self.preferences.set('from_address', self.from_address)
        return
        
            
    def _to_address_changed(self, old, new):
        if(new != None and new != Undefined):
            self.preferences.set('to_address', self.to_address)
        return
        
    ###########################################################################
    # 'Plugin' interface.
    ###########################################################################

    def start(self, application):
        """ Starts the plugin. """

        #Simple formatter. 
        #
        #By convention Envisage expects the fields in the log message to be
        #delimited by the "|" symbol and take the form: 
        #
        #        severity|date|msg 
        formatter = logging.Formatter('%(levelname)s|%(asctime)s|%(message)s')
    
        # get the log level from the application preferences
        self.level = self.preferences.get('log_level', self.level_)
        self.handler = log_queue_handler
        self.handler.setLevel(self.level_)
            
        # get the values from the preferences
        self.enable_agent = self.preferences.get('enable_agent', self.enable_agent)
        self.smtp_server = self.preferences.get('smtp_server', self.smtp_server)
        self.from_address = self.preferences.get('from_address', self.from_address)
        self.to_address = self.preferences.get('to_address', self.to_address)
    
        # set them back to make sure the preferences are initialized
        self.preferences.set('enable_agent', self.enable_agent)
        self.preferences.set('smtp_server', self.smtp_server)
        self.preferences.set('from_address', self.from_address)
        self.preferences.set('to_address', self.to_address)
        self.save_preferences()
    
        self.register_service(ILOGGER, self)
        
        return

    
    def stop(self, application):
        """ Stops the plugin. """
        
        self.save_preferences()
        return
    
#### EOF ######################################################################
