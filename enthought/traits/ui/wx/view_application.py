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
# Author: David C. Morrill
# Date: 11/10/2004
#  
#  Symbols defined: view_application
#
#------------------------------------------------------------------------------
""" Creates a wxPython specific modal dialog user interface that runs as a 
complete application, using information from the specified UI object.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

import sys

import os

# File to redirect output to. If '', output goes to stdout.
redirect_filename = ''

#-------------------------------------------------------------------------------
#  Creates a 'stand-alone' wx Application to display a specified traits UI View:  
#-------------------------------------------------------------------------------

def view_application ( context, view, kind, handler, id, scrollable, args ):
    """ Creates a stand-alone wx Application to display a specified traits UI 
        View.
    
    Parameters
    ----------
    context : object or dictionary
        A single object or a dictionary of string/object pairs, whose trait
        attributes are to be edited. If not specified, the current object is
        used.
    view : view object
        A View object that defines a user interface for editing trait attribute
        values. 
    kind : string
        The type of user interface window to create. See the 
        **enthought.traits.ui.view.kind_trait** trait for values and
        their meanings. If *kind* is unspecified or None, the **kind** 
        attribute of the View object is used.
    handler : Handler object
        A handler object used for event handling in the dialog box. If
        None, the default handler for Traits UI is used.
    scrollable : Boolean
        Indicates whether the dialog box should be scrollable. When set to 
        True, scroll bars appear on the dialog box if it is not large enough
        to display all of the items in the view at one time.
        

    """
    if (kind == 'panel') or ((kind is None) and (view.kind == 'panel')):
        kind = 'modal'
        
    app = wx.GetApp()
    if (app is None) or (not app.IsMainLoopRunning()):
        return ViewApplication( context, view, kind, handler, id, 
                                scrollable, args ).ui.result
                                
    return view.ui( context, 
                    kind       = kind, 
                    handler    = handler,
                    id         = id,
                    scrollable = scrollable,
                    args       = args ).result
    
#-------------------------------------------------------------------------------
#  'ViewApplication' class:
#-------------------------------------------------------------------------------

class ViewApplication ( wx.PySimpleApp ):
    """ Modal window that contains a stand-alone application.
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, context, view, kind, handler, id, scrollable, args ):
        """ Initializes the object.
        """
        self.context    = context
        self.view       = view
        self.kind       = kind
        self.handler    = handler
        self.id         = id
        self.scrollable = scrollable
        self.args       = args
        
        wx.InitAllImageHandlers()

        if os.environ.get( 'ENABLE_FBI' ) is not None:
            from enthought.developer.helper.fbi import enable_fbi
            enable_fbi()
            
        if redirect_filename.strip() != '':
            super( ViewApplication, self ).__init__( 1, redirect_filename )
        else:
            super( ViewApplication, self ).__init__()
         
        self.MainLoop()
    
    #---------------------------------------------------------------------------
    #  Handles application initialization:
    #---------------------------------------------------------------------------
  
    def OnInit ( self ):
        """ Handles application initialization.
        """
        self.ui = self.view.ui( self.context, 
                                kind       = self.kind, 
                                handler    = self.handler,
                                id         = self.id,
                                scrollable = self.scrollable,
                                args       = self.args )
        return True

