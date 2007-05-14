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
""" Trait definition for a wxPython-based font.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Trait, TraitHandler, TraitError
    
from enthought.traits.ui.api \
    import FontEditor

#-------------------------------------------------------------------------------
#  Convert a string into a valid 'wxFont' object (if possible):
#-------------------------------------------------------------------------------

# Mapping of strings to valid wxFont families
font_families = {
    'default':    wx.DEFAULT,
    'decorative': wx.DECORATIVE,
    'roman':      wx.ROMAN,
    'script':     wx.SCRIPT,
    'swiss':      wx.SWISS,
    'modern':     wx.MODERN
}

# Mapping of strings to wxFont styles
font_styles = {
    'slant':  wx.SLANT,
    'italic': wx.ITALIC
}

# Mapping of strings wxFont weights
font_weights = {
    'light': wx.LIGHT,
    'bold':  wx.BOLD
}

# Strings to ignore in text representations of fonts
font_noise = [ 'pt', 'point', 'family' ]

#-------------------------------------------------------------------------------
#  Converts a wx.Font into a string description of itself:  
#-------------------------------------------------------------------------------

def font_to_str ( font ):
    """ Converts a wx.Font into a string description of itself.
    """
    weight = { wx.LIGHT:  ' Light',
               wx.BOLD:   ' Bold'   }.get( font.GetWeight(), '' )
    style  = { wx.SLANT:  ' Slant',
               wx.ITALIC: ' Italic' }.get( font.GetStyle(), '' )
    underline = ''
    if font.GetUnderlined():
        underline = ' underline'
    return '%s point %s%s%s%s' % (
           font.GetPointSize(), font.GetFaceName(), style, weight, underline )
    
#-------------------------------------------------------------------------------
#  Create a TraitFont object from a string description:
#-------------------------------------------------------------------------------

def create_traitsfont ( value ):
    """ Create a TraitFont object from a string description.
    """
    if isinstance( value, wx.Font ):
        value = font_to_str( value )
        
    point_size = None
    family     = wx.DEFAULT
    style      = wx.NORMAL
    weight     = wx.NORMAL
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
            if point_size is None:
                try:
                    point_size = int( lword )
                    continue
                except:
                    pass
            facename.append( word )
    return TraitsFont( point_size or 10, family, style, weight, underline,
                    ' '.join( facename ) )

#-------------------------------------------------------------------------------
#  'TraitsFont' class:  
#-------------------------------------------------------------------------------
    
class TraitsFont ( wx.Font ):
    """ A Traits-specific wx.Font.
    """
    #---------------------------------------------------------------------------
    #  Returns the pickleable form of a TraitsFont object:
    #---------------------------------------------------------------------------
    
    def __reduce_ex__ ( self, protocol ):
        """ Returns the pickleable form of a TraitsFont object.
        """
        return ( create_traitsfont, ( font_to_str( self ), ) )

    #---------------------------------------------------------------------------
    #  Returns a printable form of the font:  
    #---------------------------------------------------------------------------
                
    def __str__ ( self ):
        """ Returns a printable form of the font.
        """
        return font_to_str( self )
        
#-------------------------------------------------------------------------------
#  'TraitWXFont' class'
#-------------------------------------------------------------------------------

class TraitWXFont ( TraitHandler ):
    """ Ensures that values assigned to a trait attribute are valid font
    descriptor strings; the value actually assigned is the corresponding 
    TraitsFont.
    """
    #---------------------------------------------------------------------------
    #  Validates that the value is a valid font:
    #---------------------------------------------------------------------------
    
    def validate ( self, object, name, value ):
        """ Validates that the value is a valid font descriptor string. If so, 
        it returns the corresponding TraitsFont; otherwise, it raises a 
        TraitError.
        """
        if value is None:
            return None
            
        try:
            return create_traitsfont( value )
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

fh     = TraitWXFont()
WxFont = Trait( create_traitsfont( 'Arial 10' ), fh, editor = FontEditor )
    
