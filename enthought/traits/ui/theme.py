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
    import Image, HasBorder, HasMargin, Alignment
    
#-------------------------------------------------------------------------------
#  'Theme' class:
#-------------------------------------------------------------------------------

class Theme ( HasPrivateTraits ):
    
    #-- Public Traits ----------------------------------------------------------
    
    # The background image to use for the theme:
    image = Image
    
    # The border inset:
    border = HasBorder
    
    # The margin to use around the content:
    content = HasMargin
    
    # The margin to use around the label:
    label = HasMargin
    
    # The alignment to use for positioning the label:
    alignment = Alignment
    
    # Note: The 'content_color' and 'label_color' traits should be added by a
    # toolkit-specific category...
    
    #-- Constructor ------------------------------------------------------------
    
    def __init__ ( self, image = None, **traits ):
        """ Initializes the object.
        """
        if image is not None:
            self.image = image
            
        super( Theme, self ).__init__( **traits )
        
# Create a default theme:
default_theme = Theme()
        
