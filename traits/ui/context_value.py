#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
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
#  Date:   08/18/2008
#
#------------------------------------------------------------------------------

""" Defines some helper classes and traits used to define 'bindable' editor
    values.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import HasPrivateTraits, Instance, Str, Int, Float, Either

#-------------------------------------------------------------------------------
#  'ContextValue' class:
#-------------------------------------------------------------------------------

class ContextValue ( HasPrivateTraits ):
    """ Defines the name of a context value that can be bound to some editor
        value.
    """

    # The extended trait name of the value that can be bound to the editor
    # (e.g. 'selection' or 'handler.selection'):
    name = Str

    #-- object Interface -------------------------------------------------------

    def __init__ ( self, name ):
        """ Initializes the object.
        """
        self.name = name

# Define a shorthand name for a ContextValue:
CV = ContextValue

#-------------------------------------------------------------------------------
#  Trait definitions useful in defining bindable editor traits:
#-------------------------------------------------------------------------------

InstanceOfContextValue = Instance( ContextValue, allow_none = False )

def CVType( type ):
    return Either( type, InstanceOfContextValue, sync_value = 'to' )

CVInt   = CVType( Int )
CVFloat = CVType( Float )
CVStr   = CVType( Str )

