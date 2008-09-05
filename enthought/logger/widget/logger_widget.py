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
import datetime
import os
import wx

# Enthought library imports.
from enthought.util.resource import get_path
from log_detail_view import LogDetailView, FullLogView
from wx import TheClipboard, TextDataObject


LEVEL_COLUMN = 0
DATE_COLUMN = 1
TIME_COLUMN = 2
MESSAGE_COLUMN = 3


class LoggerWidget(wx.Panel):
    """ A LoggerListWidget with a reset button. """
    
    _listControl = None
    

    def __init__(self, parent, service):
        wx.Panel.__init__(self, parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.service = service

        # create list widget
        self._listControl = LoggerListWidget(self, self.service)
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
        return self.service.handler.formatter.format(log_record)


class LoggerListWidget(wx.ListCtrl):
    """A logger widget displaying entried from the logger in a list control."""

    import logging
    map = {'DEBUG': logging.DEBUG,
           'INFO' : logging.INFO,
           'WARNING' : logging.WARNING,
           'ERROR' : logging.ERROR,
           'CRITICAL' : logging.CRITICAL}
    inverse_map = {
        logging.DEBUG: 'DEBUG',
        logging.INFO: 'INFO',
        logging.WARNING: 'WARNING',
        logging.ERROR: 'ERROR',
        logging.CRITICAL: 'CRITICAL',
    }

    def __init__(self, parent, service):
        
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT |
                                                     wx.LC_VIRTUAL |
                                                     wx.LC_HRULES |
                                                     wx.LC_VRULES)
                            
        self.service = service

        # by default do nothing when a user double clicks on a record ...
        self._selection_action = None

        self.levels = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
        self._make_icons()
        
        self.InsertColumn(LEVEL_COLUMN, "Level")
        self.InsertColumn(DATE_COLUMN, "Date")
        self.InsertColumn(TIME_COLUMN, "Time")
        self.InsertColumn(MESSAGE_COLUMN, "Message")
        self.SetColumnWidth(LEVEL_COLUMN, 100)
        self.SetColumnWidth(DATE_COLUMN, 90)
        self.SetColumnWidth(TIME_COLUMN, 110)
        self.SetColumnWidth(MESSAGE_COLUMN, 650)

        self.SetItemCount(self.service.handler.size)

        # set event handlers
        wx.EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)

        # set the view to update when something is logged.
        self.service.handler._view = self

        self.log_records = []

        self.during_update = False


    def set_selection_action(self, action):
        """ What do we call/construct when a user double clicks on a record?
            action will be called/constructed with (parent, title, message).
        """  
        self._selection_action = action
        
        return 

        
    def OnReset(self, event):
        """ Removes all entries from the list. """
        self.service.handler.reset() 
        self.DeleteAllItems()
        self.SetItemCount(self.service.handler.size)
        self.Refresh()
        return 

    def IsVirtual(self):
        return True


    #### Callbacks for the list... ############################################

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex
        msg = self._complete_message(self.currentItem)
        if msg is not "" and self._selection_action is not None:
            dlg = self._selection_action(parent=self, msg=msg,
                service=self.service)
            val = dlg.open()
        return
        

    def OnGetItemText(self, item, col):
        if item < len(self.log_records):
            item = len(self.log_records) - item - 1
            result = self._parse_record(self.log_records[item], col)
        else:
            result = ''
        return result    
            

    def OnGetItemImage(self, item):
        if item < len(self.log_records):
            item = len(self.log_records) - item - 1
            index = self.levels.index(self.log_records[item].levelname)
        else:
            index = -1

        return index


    def update(self):
        """ Update the table if new records are available.
        """
        if self.service.handler.has_new_records() and not self.during_update:
            self.really_update()


    def really_update(self):
        """ Update whether the handler has new records or not.

        This allows for changes in the log level to trigger an update of the
        table.
        """
        self.log_records = self._filter_records(self.service.handler.get())
        num_rec = len(self.log_records)
        # This seems to cause a required repaint? 
        self.SetItemCount(self.service.handler.size)
        # Focus on the last item.
        self.EnsureVisible(0)
        self.Refresh()


    ### Utility methods #######################################################    

    def _filter_records(self, records):
        """Filters out records that are lower than our plugin log level.
        """
        filtered_records = []

        for rec in records:
            if rec.levelno >= self.service.preferences.level_:
                filtered_records.append(rec)

        return filtered_records


    def _parse_record(self, rec, column):
        """ Parse a record into items for display on the table.
        """
        if column == LEVEL_COLUMN:       
            # Add a space to the level name for display.
            level = ' '+ rec.levelname
            return level
        elif column == MESSAGE_COLUMN:
            msg = rec.getMessage()
            # Just display the first line of multiline messages, like stacktraces.
            msgs = msg.strip().split('\n')

            if len(msgs) > 1:
                suffix = '... [double click for details]'
            else:
                suffix = ''

            abbrev_msg = msgs[0] + suffix
            return abbrev_msg
        else:
            dt = datetime.datetime.fromtimestamp(rec.created)
            if column == DATE_COLUMN:
                date = dt.date().isoformat()
                return date
            elif column == TIME_COLUMN:
                time = dt.time().isoformat()
                return time
            else:
                raise ValueError("Unexpected column %r" % column)


    def _complete_message(self, irec):
        length = len(self.log_records)
        if irec < length:
            msg = self.log_records[length - 1 - irec].getMessage()
        else:
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

