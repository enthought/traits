#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   07/13/2007
#
#-------------------------------------------------------------------------------

""" Defines 'theme' related classes.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import HasPrivateTraits

from .ui_traits import Image, HasBorder, HasMargin, Alignment

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
    alignment = Alignment( cols = 4 )

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

