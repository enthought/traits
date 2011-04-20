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
#  Date:   10/25/2004
#
#------------------------------------------------------------------------------

""" Defines various helper functions that are useful for creating Traits-based
    user interfaces.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from string import uppercase, lowercase

from ..api import BaseTraitHandler, CTrait, Enum, TraitError

from .ui_traits import SequenceTypes

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

# Docking drag bar style:
DockStyle = Enum( 'horizontal', 'vertical', 'tab', 'fixed' )

#----------------------------------------------------------------------------
#  Return a 'user-friendly' name for a specified trait:
#----------------------------------------------------------------------------

def user_name_for ( name ):
    """ Returns a "user-friendly" name for a specified trait.
    """
    name       = name.replace( '_', ' ' )
    name       = name[:1].upper() + name[1:]
    result     = ''
    last_lower = 0
    for c in name:
        if (c in uppercase) and last_lower:
           result += ' '
        last_lower = (c in lowercase)
        result    += c
    return result

#-------------------------------------------------------------------------------
#  Format a number with embedded commas:
#-------------------------------------------------------------------------------

def commatize ( value ):
    """ Formats a specified value as an integer string with embedded commas.
        For example: commatize( 12345 ) returns "12,345".
    """
    s = str( abs( value ) )
    s = s.rjust( ((len( s ) + 2) / 3) * 3 )
    result = ','.join( [ s[ i: i+3 ] for i in range( 0, len(s), 3 ) ] ).lstrip()
    if value >= 0:
        return result

    return '-' + result

#-------------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------------

def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance( values, dict ):
        data = [ ( unicode( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
            col = data[0][0].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CTrait ):
            handler = handler.handler
        if not isinstance( handler, BaseTraitHandler ):
            raise TraitError, "Invalid value for 'values' specified"
        if handler.is_mapped:
            data = [ ( unicode( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
        else:
            data = [ ( unicode( v ), v ) for v in handler.values ]
    else:
        data = [ ( unicode( v ), v ) for v in values ]

    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name

    return ( names, mapping, inverse_mapping )
