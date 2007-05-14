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
# Date: 10/21/2004
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines various directory editor and the directory editor factory for the 
wxPython user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from file_editor import ToolkitEditorFactory as EditorFactory
from file_editor import SimpleEditor         as SimpleFileEditor

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for directory editors.
    """
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
                                      
    def custom_editor ( self, ui, object, name, description, parent ):
        return self.simple_editor( ui, object, name, description, parent )
        
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( SimpleFileEditor ):
    """ Simple style of editor for directories, which displays a text field
    and a **Browse** button that opens a directory-selection dialog box.
    """
    #---------------------------------------------------------------------------
    #  Creates the correct type of file dialog:
    #---------------------------------------------------------------------------
           
    def create_file_dialog ( self ):
        """ Creates the correct type of file dialog.
        """
        dlg =  wx.DirDialog( self.control, message = 'Select a Directory' )
        dlg.SetPath( self._filename.GetValue() )
        return dlg
        
