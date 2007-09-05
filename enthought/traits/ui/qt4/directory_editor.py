#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines various directory editor and the directory editor factory for the 
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

from file_editor \
    import ToolkitEditorFactory as EditorFactory,    \
           SimpleEditor         as SimpleFileEditor, \
           CustomEditor         as CustomFileEditor

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for directory editors.
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
        return CustomEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
        
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
        dlg = QtGui.QFileDialog(self.control)
        dlg.selectFile(self._filename.text())
        dlg.setFileMode(QtGui.QFileDialog.Directory)

        return dlg
        
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( CustomFileEditor ):
    """ Custom style of editor for directories, which displays a tree view of
        the file system.
    """

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object(self, idx):
        """ Handles the user changing the contents of the edit control.
        """
        if self._model.isDir(idx):
            self.value = unicode(self._model.filePath(idx))
