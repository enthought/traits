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

""" Defines the concrete implementations of the traits Toolkit interface for
    the 'null' (do nothing) user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..toolkit import Toolkit

from ..editor_factory import EditorFactory

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Create a dummy singleton editor factory:
null_editor_factory = EditorFactory()

#-------------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------------

class GUIToolkit ( Toolkit ):

    #---------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #---------------------------------------------------------------------------

    def color_trait ( self, *args, **traits ):
        from . import color_trait as ct
        return ct.NullColor( *args, **traits )

    def rgb_color_trait ( self, *args, **traits ):
        from . import rgb_color_trait as rgbct
        return rgbct.RGBColor( *args, **traits )

    def font_trait ( self, *args, **traits ):
        from . import font_trait as ft
        return ft.NullFont( *args, **traits )

    def kiva_font_trait ( self, *args, **traits ):
        from . import font_trait as ft
        return ft.NullFont( *args, **traits )

    def constants ( self, *args, **traits ):
        constants = {'WindowColor': ( 236 / 255.0, 233 / 255.0, 216 / 255.0, 1.0 )}
        return constants

    #---------------------------------------------------------------------------
    #  'EditorFactory' factory methods:
    #---------------------------------------------------------------------------

    def __getattribute__(self, attr):
        """ Return a method that returns null_editor_factory for any request to
        an unimplemented ``*_editor()`` method.

        This must be __getattribute__ to make sure that we override the
        definitions in the superclass which raise NotImplementedError.
        """
        if attr.endswith('_editor'):
            return lambda *args, **kwds: null_editor_factory
        else:
            return super(GUIToolkit, self).__getattribute__(attr)

