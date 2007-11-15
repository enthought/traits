#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
# 
#  Author: David C. Morrill
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

""" Defines functions and classes used to create pop-up file dialogs for
    opening and saving files.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import isfile
    
from enthought.traits.api \
    import HasPrivateTraits, File, List, Str, Int, Instance, Property, Button
    
from enthought.traits.ui.api \
    import View, VGroup, HGroup, Item, Handler, FileEditor
    
# fixme: The HistoryEditor needs to be added to the toolkit...    
from enthought.traits.ui.wx.history_editor \
    import HistoryEditor
    
#-------------------------------------------------------------------------------
#  'OpenFileDialog' class:
#-------------------------------------------------------------------------------

class OpenFileDialog ( Handler ):
    
    # The starting and current file path:
    file_name = File
    
    # The list of file filters to apply:
    filter = List( Str )
    
    # Number of history entries to allow:
    entries = Int( 10 )
    
    # The file dialog title:
    title = Str( 'Open File' )
    
    # The Traits UI persistence id to use:
    id = Str( 'enthought.traits.ui.file_dialog.OpenFileDialog' )
    
    #-- Private Traits ---------------------------------------------------------
    
    # Is the currently specified file name valid?
    is_valid_file = Property( depends_on = 'file_name' )
    
    # The OK and Cancel buttons:
    ok     = Button( 'OK' )
    cancel = Button( 'Cancel' )
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_is_valid_file ( self ):
        return isfile( self.file_name )
        
    #-- Handler Event Handlers -------------------------------------------------
    
    def object_ok_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        info.ui.dispose( True )
        
    def object_cancel_changed ( self, info ):
        """ Handles the user clicking the Cancel button.
        """
        info.ui.dispose( False )
        
    #-- Private Methods --------------------------------------------------------
    
    def trait_view ( self, name = None, view_element = None ):
        """ Returns the file dialog view to use.
        """
        return View(
            VGroup(
                VGroup(
                    Item( 'file_name', 
                          style      = 'custom',
                          show_label = False,
                          editor     = FileEditor( filter = self.filter )
                    )
                ),
                HGroup(
                    Item( 'file_name',
                          id      = 'history',
                          editor  = HistoryEditor( entries  = self.entries,
                                                   auto_set = True ),
                          springy = True
                    ),
                    Item( 'ok',
                          show_label   = False,
                          enabled_when = 'is_valid_file'
                    ),
                    Item( 'cancel',
                          show_label = False
                    )
                )
            ),
            title     = self.title,
            id        = self.id,
            kind      = 'livemodal',
            width     = 0.20,
            height    = 0.20,
            resizable = True
        )
        
#-------------------------------------------------------------------------------
#  Returns a file name to open or None if the user cancelled the operation:  
#-------------------------------------------------------------------------------

def open_file ( **traits ):
    fd = OpenFileDialog( **traits )
    if fd.edit_traits().result:
        return fd.file_name
        
    return None
    
#-- Test Case ------------------------------------------------------------------

if __name__ == '__main__':
    print open_file()

