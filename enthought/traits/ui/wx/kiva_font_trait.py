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
# Date: 12/22/2004
#------------------------------------------------------------------------------
""" Trait definition for a wxPython-based Kiva font.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Trait, TraitError, TraitHandler
    
from enthought.traits.ui.api \
    import KivaFontEditor

#-------------------------------------------------------------------------------
#  Convert a string into a valid 'Font' object (if possible):
#-------------------------------------------------------------------------------
    
# Strings to ignore in text representations of fonts
font_noise = [ 'pt', 'point', 'family' ]

font_families = font_styles = font_weights = DEFAULT = NORMAL = None

def init_constants ( ):
    """ Dynamically load Kiva constants to avoid import dependencies.
    """
    global font_families, font_styles, font_weights, DEFAULT, NORMAL
    
    if font_families is not None:
        return
        
    import enthought.kiva.constants as kc
    
    DEFAULT = kc.DEFAULT
    NORMAL  = kc.NORMAL
    
    # Mapping of strings to valid Kiva font families:
    font_families = {
        'default':    kc.DEFAULT,
        'decorative': kc.DECORATIVE,
        'roman':      kc.ROMAN,
        'script':     kc.SCRIPT,
        'swiss':      kc.SWISS,
        'modern':     kc.MODERN
    }
    
    # Mapping of strings to Kiva font styles:
    font_styles = {
        'italic': kc.ITALIC
    }
    
    # Mapping of strings to Kiva font weights:
    font_weights = {
        'bold': kc.BOLD
    }

#-------------------------------------------------------------------------------
#  'TraitKivaFont' class'
#-------------------------------------------------------------------------------

class TraitKivaFont ( TraitHandler ):
    """ Ensures that values assigned to a trait attribute are valid font
    descriptor strings for Kiva fonts; the value actually assigned is the 
    corresponding Kiva font.
    """
    #---------------------------------------------------------------------------
    #  Validates that the value is a valid font:
    #---------------------------------------------------------------------------
    
    def validate ( self, object, name, value ):
        """ Validates that the value is a valid font.
        """
        from enthought.kiva.fonttools import Font
        
        if isinstance( value, Font ):
            return value
        
        # Make sure all Kiva related data is loaded: 
        init_constants()
        
        try:
            point_size = 10
            family     = DEFAULT
            style      = NORMAL
            weight     = NORMAL
            underline  = 0
            facename   = []
            for word in value.split():
                lword = word.lower()
                if font_families.has_key( lword ):
                    family = font_families[ lword ]
                elif font_styles.has_key( lword ):
                    style = font_styles[ lword ]
                elif font_weights.has_key( lword ):
                    weight = font_weights[ lword ]
                elif lword == 'underline':
                    underline = 1
                elif lword not in font_noise:
                    try:
                        point_size = int( lword )
                    except:
                        facename.append( word )
                        
            return Font( point_size, family, weight, style, underline, 
                         ' '.join( facename ) )
        except:
            pass
            
        raise TraitError, ( object, name, 'a font descriptor string',
                            repr( value ) )

    def info ( self ):                              
        return ( "a string describing a font (e.g. '12 pt bold italic "
                 "swiss family Arial' or 'default 12')" )

#-------------------------------------------------------------------------------
#  Define a wxPython specific font trait:
#-------------------------------------------------------------------------------

fh = TraitKivaFont()
try:
    KivaFont = Trait( fh.validate( None, None, 'modern 12' ), fh, 
                      editor = KivaFontEditor )
except:
    from enthought.traits.traits import TraitImportError
    
    KivaFont = TraitImportError( "The enthought.kiva package needs to be "
                   "installed before the KivaFont trait can be used" )
    
