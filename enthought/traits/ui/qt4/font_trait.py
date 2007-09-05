#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Trait definition for a PyQt-based font.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

from enthought.traits.api \
    import Trait, TraitHandler, TraitError
    
from enthought.traits.ui.api \
    import FontEditor

#-------------------------------------------------------------------------------
#  Convert a string into a valid 'wxFont' object (if possible):
#-------------------------------------------------------------------------------

# Mapping of strings to valid QFont style hints.
font_families = {
    'default':    QtGui.QFont.AnyStyle,
    'decorative': QtGui.QFont.Decorative,
    'roman':      QtGui.QFont.Serif,
    'script':     QtGui.QFont.SansSerif,
    'swiss':      QtGui.QFont.SansSerif,
    'modern':     QtGui.QFont.TypeWriter
}

# Mapping of strings to QFont styles.
font_styles = {
    'slant':  QtGui.QFont.StyleOblique,
    'italic': QtGui.QFont.StyleItalic
}

# Mapping of strings to QFont weights.
font_weights = {
    'light': QtGui.QFont.Light,
    'bold':  QtGui.QFont.Bold
}

# Strings to ignore in text representations of fonts
font_noise = [ 'pt', 'point', 'family' ]

#-------------------------------------------------------------------------------
#  Converts a wx.Font into a string description of itself:  
#-------------------------------------------------------------------------------

def font_to_str ( font ):
    """ Converts a QFont into a string description of itself.
    """
    weight = { QtGui.QFont.Light:  ' Light',
               QtGui.QFont.Bold:   ' Bold'   }.get(font.weight(), '')
    style  = { QtGui.QFont.StyleOblique:  ' Slant',
               QtGui.QFont.StyleItalic:   ' Italic' }.get(font.style(), '')
    underline = ''
    if font.underline():
        underline = ' underline'
    return '%s point %s%s%s%s' % (
           font.pointSize(), unicode(font.family()), style, weight, underline )
    
#-------------------------------------------------------------------------------
#  Create a TraitFont object from a string description:
#-------------------------------------------------------------------------------

def create_traitsfont(value):
    """ Create a TraitFont object from a string description.
    """
    if isinstance(value, QtGui.QFont):
        return TraitsFont(value)

    point_size = None
    family     = ''
    style      = QtGui.QFont.StyleNormal
    weight     = QtGui.QFont.Normal
    underline  = False
    facename   = []

    for word in value.split():
        lword = word.lower()
        if font_families.has_key(lword):
            f = QtGui.QFont()
            f.setStyleHint(font_families[lword])
            family = f.defaultFamily()
        elif font_styles.has_key(lword):
            style = font_styles[lword]
        elif font_weights.has_key(lword):
            weight = font_weights[lword]
        elif lword == 'underline':
            underline = True
        elif lword not in font_noise:
            if point_size is None:
                try:
                    point_size = int(lword)
                    continue
                except:
                    pass
            facename.append(word)

    if facename:
        family = ' '.join(facename)

    if family:
        fnt = TraitsFont(family)
    else:
        fnt = TraitsFont()

    fnt.setStyle(style)
    fnt.setWeight(weight)
    fnt.setUnderline(underline)

    if point_size is not None:
        fnt.setPointSize(point_size)

    return fnt

#-------------------------------------------------------------------------------
#  'TraitsFont' class:  
#-------------------------------------------------------------------------------
    
class TraitsFont(QtGui.QFont):
    """ A Traits-specific QFont.
    """
    #---------------------------------------------------------------------------
    #  Returns the pickleable form of a TraitsFont object:
    #---------------------------------------------------------------------------
    
    def __reduce_ex__(self, protocol):
        """ Returns the pickleable form of a TraitsFont object.
        """
        return (create_traitsfont, (font_to_str(self), ))

    #---------------------------------------------------------------------------
    #  Returns a printable form of the font:  
    #---------------------------------------------------------------------------

    def __str__(self):
        """ Returns a printable form of the font.
        """
        return font_to_str(self)
        
#-------------------------------------------------------------------------------
#  'TraitPyQtFont' class'
#-------------------------------------------------------------------------------

class TraitPyQtFont ( TraitHandler ):
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
#  Define a PyQt specific font trait:
#-------------------------------------------------------------------------------

PyQtFont = Trait(TraitsFont(), TraitPyQtFont(), editor=FontEditor)
