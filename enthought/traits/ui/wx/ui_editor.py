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
# 
#  Date: 03/03/2006
# 
#  Symbols defined: UIEditor
#
#------------------------------------------------------------------------------
""" Defines the BasicUIEditor class, which allows creating editors that define
their function by creating an embedded Traits UI.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Instance
    
from enthought.traits.ui.api \
    import UI
    
from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'UIEditor' base class:
#-------------------------------------------------------------------------------

class UIEditor ( Editor ):
    """ An editor that creates an embedded Traits UI.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # The Traits UI created by the editor
    ui = Instance( UI )
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.ui      = self.init_ui( parent )
        self.control = self.ui.control
        
    #---------------------------------------------------------------------------
    #  Creates the traits UI for the editor (must be overridden by a subclass):  
    #---------------------------------------------------------------------------
                
    def init_ui ( self, parent ):
        """ Creates the traits UI for the editor.
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        # Do nothing, since the imbedded traits UI should handle the updates
        # itself, without our meddling:
        pass
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Make sure the imbedded traits UI is disposed of properly:
        if self.ui is not None:
            self.ui.dispose()
            
        super( UIEditor, self ).dispose()
        
#-- UI preference save/restore interface ---------------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the 
    #  editor:
    #---------------------------------------------------------------------------
            
    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the 
            editor.
        """
        self.ui.set_prefs( prefs )
            
    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------
            
    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return self.ui.get_prefs()
        
#-- End UI preference save/restore interface -----------------------------------                         
        
