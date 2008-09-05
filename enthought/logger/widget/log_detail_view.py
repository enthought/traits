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
import sys

# Major library imports.
import wx

# Enthought library imports.
from enthought.pyface.api import Dialog
from enthought.traits.api import Any, Str, Tuple


class TextView(Dialog):

    msg = Str('')
    
    # The associated LoggerService. This is unused in this class, but we include
    # it to match the interface of the QualityAgent.
    service = Any()
    size = Tuple((640, 480))
    title = Str('Text') 
    style = 'modal'

    
    #### Dialog interface. #####################################################

    def _create_contents(self, parent):
        """ Creates the window contents.
        """
        dialog = parent

        sizer = wx.BoxSizer(wx.VERTICAL)
        dialog.SetSizer(sizer)
        dialog.SetAutoLayout(True)

        # The 'guts' of the dialog.
        dialog_area = self._create_dialog_area(dialog)
        sizer.Add(dialog_area, 1, wx.EXPAND | wx.ALL, 5)

        # Resize the dialog to match the sizer's minimal size.
        if self.size != (-1,-1):
            dialog.SetSize(self.size)
        else:
            sizer.Fit(dialog)

        dialog.SetSizeHints(minW=300, minH=350)
        dialog.CentreOnParent()
 
    def _create_dialog_area(self, parent):
        """ Creates the main content of the dialog. """
        # Add the main panel 
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(parent, -1)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        
        # Add the log details view ...
        style = (wx.TE_MULTILINE |
                 wx.TE_READONLY |
                 wx.VSCROLL |
                 wx.TE_RICH2 |
                 wx.TE_WORDWRAP)
        details = wx.TextCtrl(panel, -1, self.msg, style=style)
        # Set the font to not be proportional 
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        details.SetStyle(0, len(self.msg), wx.TextAttr(font=font))
        sizer.Add(details, 1, wx.EXPAND | wx.ALL, 5)

        # 'Close' button.
        close = wx.Button(panel, wx.ID_CANCEL, "Close")
        close.SetDefault()
        wx.EVT_BUTTON(panel, wx.ID_CANCEL, self._wx_on_cancel)
        sizer.Add(close, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.TOP, 5)
        
        return panel



###############################################################################
# Dialog to display a log message
###############################################################################
class LogDetailView(TextView):

    title = Str('Log Message Detail') 

###############################################################################
# Dialog to display the full log
###############################################################################
class FullLogView(TextView):

    size = Tuple((640, 480))
    title = Str('Log Messages') 

####### EOF #############################################################
