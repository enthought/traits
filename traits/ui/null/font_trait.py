#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   02/14/2005
#
#------------------------------------------------------------------------------

""" Trait definition for a null-based (i.e., no UI) font.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Trait, TraitHandler, TraitError

#-------------------------------------------------------------------------------
#  Convert a string into a valid 'wxFont' object (if possible):
#-------------------------------------------------------------------------------

# Mapping of strings to valid wxFont families
font_families = [
    'default',
    'decorative',
    'roman',
    'script',
    'swiss',
    'modern'
]

# Mapping of strings to wxFont styles
font_styles = [
    'slant',
    'italic'
]

# Mapping of strings wxFont weights
font_weights = [
    'light',
    'bold'
]

# Strings to ignore in text representations of fonts
font_noise = [ 'pt', 'point', 'family' ]

#-------------------------------------------------------------------------------
#  'TraitFont' class'
#-------------------------------------------------------------------------------

class TraitFont ( TraitHandler ):
    """ Ensures that values assigned to a trait attribute are valid font
    descriptor strings; the value actually assigned is the corresponding
    canonical font descriptor string.
    """
    #---------------------------------------------------------------------------
    #  Validates that the value is a valid font:
    #---------------------------------------------------------------------------

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid font descriptor string.
        """
        try:
            point_size = family = style = weight = underline = ''
            facename   = []
            for word in value.split():
                lword = word.lower()
                if lword in font_families:
                    family = ' ' + lword
                elif lword in font_styles:
                    style = ' ' + lword
                elif lword in font_weights:
                    weight = ' ' + lword
                elif lword == 'underline':
                    underline = ' ' + lword
                elif lword not in font_noise:
                    try:
                        int( lword )
                        point_size = lword + ' pt'
                    except:
                        facename.append( word )
            return ('%s%s%s%s%s%s' % ( point_size, family, style, weight,
                    underline, ' '.join( facename ) )).strip()
        except:
            pass
        raise TraitError, ( object, name, 'a font descriptor string',
                            repr( value ) )

    def info ( self ):
        return ( "a string describing a font (e.g. '12 pt bold italic "
                 "swiss family Arial' or 'default 12')" )

#-------------------------------------------------------------------------------
#  Define a 'null' specific font trait:
#-------------------------------------------------------------------------------

### Note: Declare the editor to be a function which returns the FontEditor
# class from traits ui to avoid circular import issues. For backwards
# compatibility with previous Traits versions, the 'editors' folder in Traits
# project declares 'from api import *' in its __init__.py. The 'api' in turn
# can contain classes that have a Font trait which lead to this file getting
# imported. This leads to a circular import when declaring a Font trait.
def get_font_editor(*args, **traits):
    from ..api import FontEditor
    return FontEditor(*args, **traits)

fh       = TraitFont()
NullFont = Trait( fh.validate( None, None, 'Arial 10' ), fh,
                  editor = get_font_editor )

