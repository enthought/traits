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

# Standard library imports.
import os
import wx

# Enthought library imports.
from enthought.logger.log_queue_handler import log_queue_handler
from enthought.logger.plugin.logger_plugin import LoggerPlugin
from enthought.util.resource import get_path
from enthought.envisage import get_application
from log_detail_view import LogDetailView, FullLogView
from wx import TheClipboard, TextDataObject

class LoggerWidget(wx.Panel):
    """ A LoggerListWidget with a reset button. """
    
    _listControl = None
    

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # create list widget
        self._listControl = LoggerListWidget(self)
        sizer.Add(self._listControl, 1, wx.EXPAND)

        # Add a lower horizontal sizer
        lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lower_sizer, 0, wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, 5)

        # add reset button
        reset = wx.Button(self, -1, "Reset Logs")
        wx.EVT_BUTTON(self, reset.GetId(), self._listControl.OnReset)
        lower_sizer.Add(reset, 0, wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, 5)
        
        # add complete log text button
        show_logs = wx.Button(self, -1, "Complete Log Text")
        wx.EVT_BUTTON(self, show_logs.GetId(), self.show_logs)
        lower_sizer.Add(show_logs, 0, wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, 5)
        
        # add copy log to clipboard button
        copy_logs = wx.Button(self, -1, "Copy Log to ClipBoard")
        wx.EVT_BUTTON(self, copy_logs.GetId(), self.copy_log_to_clipboard)
        lower_sizer.Add(copy_logs, 0, wx.ALIGN_LEFT | wx.TOP | wx.BOTTOM, 5)
        
        # set the default double-click action
        self.set_selection_action(LogDetailView)

        sizer.Fit(self)
        return

    
    def set_selection_action(self, action):
        """ Convenience method... See LoggerListWidget.set_selection_action
            for details.
        """  
        self._listControl.set_selection_action(action)
        
        return

    def show_logs(self, event):
        """ "Complete Log Text" Button callback. Displays the current log 
            file in a dialog.
        """
        msg = self.get_all_records()
        dlg = FullLogView(parent=self, msg=msg) 
        val = dlg.open()

        return

    def copy_log_to_clipboard(self, event):
        """ "Copy Log to ClipBoard" Button callback.
        """
        TheClipboard.Open()
        TheClipboard.SetData(TextDataObject(self.get_all_records()))
        TheClipboard.Close()

        return

    def get_all_records(self):
        """ Returns a mutli-line string with all log records formated.
        """
        return '\n'.join(self.format_record(r) 
                                for r in self._listControl.log_records)


    def format_record(self, log_record):
        """ Returns a string with the relevant info out of a log_record object.
        """
        # FIXME: I don't think this should be in here, it should be
        # somewhere in enthought.logger, probably factored out with the
        # code writing to the log file (which I couldn't find)
        return "%s|%s|%s" %(log_record.levelname, 
                            log_record.asctime,
                            log_record.message)

class LoggerListWidget(wx.ListCtrl):
    """A logger widget displaying entried from the logger in a list control."""

    import logging
    map = {'DEBUG': logging.DEBUG,
           'INFO' : logging.INFO,
           'WARNING' : logging.WARNING,
           'ERROR' : logging.ERROR,
           'CRITICAL' : logging.CRITICAL}

    def __init__(self, parent):
        
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT |
                                                     wx.LC_VIRTUAL |
                                                     wx.LC_HRULES |
                                                     wx.LC_VRULES)
                            
        # by default do nothing when a user double clicks on a record ...
        self._selection_action = None

        self.levels = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
        self._make_icons()
        
        self.InsertColumn(0, "Level")
        self.InsertColumn(1, "Date")
        self.InsertColumn(2, "Time")
        self.InsertColumn(3, "Message")
        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 75)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, 650)

        self.SetItemCount(log_queue_handler.size)

        # set event handlers
        wx.EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)

        # set the view to update when something is logged.
        log_queue_handler._view = self


    def set_selection_action(self, action):
        """ What do we call/construct when a user double clicks on a record?
            action will be called/constructed with (parent, title, message).
        """  
        self._selection_action = action
        
        return 

        
    def OnReset(self, event):
        """ Removes all entries from the list. """
        log_queue_handler.reset() 
        self.DeleteAllItems()
        self.SetItemCount(log_queue_handler.size)
        self.Refresh()
        return 

        
    #### Callbacks for the list... ############################################

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        msg = self._complete_message(self.currentItem)
        if msg is not "" and self._selection_action is not None:
            dlg = self._selection_action(parent=self, msg=msg)
            val = dlg.open()
        return
        

    def OnGetItemText(self, item, col):
        try:
            txt = self._parse_record(self.log_records[item])
            result = txt[col]
        except Exception, msg:
            result = ''
        
        return result    
            

    def OnGetItemImage(self, item):
        # todo - hardcoded column number - bad
        text = self.OnGetItemText(item, 0)
 
        try:
            index = self.levels.index(text.strip())
        except Exception, msg:
            index = -1
            
        return index

            
    def update(self):
        if log_queue_handler.has_new_records():
            self.log_records = self._filter_records(log_queue_handler.get())
            num_rec = len(self.log_records)
            # this seems to cause a required repaint? 
            self.SetItemCount(log_queue_handler.size)
            self.EnsureVisible(num_rec)
            self.Refresh()
        return
                
    
    ### Utility methods #######################################################    

    def _filter_records(self, records):
        """Filters out records that are lower than our plugin log level."""
        filtered_records = []
        
        for rec in records:
            log = self._parse_record(rec)
            if self.map[log[0].strip()] >= LoggerPlugin.instance.level_:
                filtered_records.append(rec)

        return filtered_records
        
    
    def _parse_record(self, rec):
        # todo can we use a custom formatter to do this more configurably?
        txt = log_queue_handler.format(rec)
        level, ymdhms, msg = txt.split('|')
        
        # split the time into date and then time 
        date, time = ymdhms.strip().split()
        
        # just display the first line of the stacktrace 
        msgs = msg.strip().split('\n')
            
        if len(msgs) > 1:
            suffix = '... [double click for details]'
        else:
            suffix = ''
            
        abbrev_msg = msgs[0] + suffix
        
        # add a space ... 
        level = ' ' + level
        
        # order the columns for display 
        recs = [level, date, time, abbrev_msg]
        
        return recs
        
        
    def _complete_message(self, rec):
        try:
            txt = log_queue_handler.format(self.log_records[rec])
            level, ymdhms, msg = txt.split('|')
        except:
            msg = ""
        return msg
        

    def _make_icons(self):
        self.il = wx.ImageList(16, 16)
        self.path = get_path(self)
   
        self.il.Add(self._get_icon('images/bug_yellow.png'))
        self.il.Add(self._get_icon('images/about.png'))
        self.il.Add(self._get_icon('images/warning.png'))
        self.il.Add(self._get_icon('images/error.png'))
        self.il.Add(self._get_icon('images/crit_error.png'))

        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        return

        
    def _get_icon(self, name):
        
        # Item icon.
        image = wx.Image(os.path.join(self.path,name), wx.BITMAP_TYPE_ANY)
        return image.ConvertToBitmap()

####EOF##################################################################

