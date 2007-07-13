#-------------------------------------------------------------------------------
#  
#  Defines 'theme' related classes.
#  
#  Written by: David C. Morrill
#  
#  Date: 07/13/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, Tuple, Int
    
from ui_traits \
    import Image, HasMargins, Margins, Alignment
    
#-------------------------------------------------------------------------------
#  'Theme' class:
#-------------------------------------------------------------------------------

class Theme ( HasPrivateTraits ):
    
    #-- Public Traits ----------------------------------------------------------
    
    # The background image to use for the theme:
    image = Image
    
    # The margins to use around the content:
    margins = HasMargins( Margins( 4, 2 ) )
    
    # The offset to use to properly position content: 
    offset = Tuple( Int, Int )
    
    # The alignment to use for positioning content:
    alignment = Alignment
    
    #-- Constructor ------------------------------------------------------------
    
    def __init__ ( self, image = None, **traits ):
        """ Initializes the object.
        """
        if image is not None:
            self.image = image
            
        super( Theme, self ).__init__( **traits )
        
# Create a default theme:
default_theme = Theme()
        
