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
#  Date:   11/22/2004
#
#------------------------------------------------------------------------------

""" Defines a subclass of the base color editor factory, for colors
    that are represented as tuples of the form ( *red*, *green*, *blue* ),
    where *red*, *green* and *blue* are floats in the range from 0.0 to 1.0.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from .color_editor import ToolkitEditorFactory as EditorFactory

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Factory for editors for RGB colors.
    """
    pass

# Define the RGBColorEditor class
# The function will try to return the toolkit-specific editor factory (located
# in enthought.traits.ui.<toolkit>.rgb_color_editor, and if none is found, the
# ToolkitEditorFactory declared here is returned.
def RGBColorEditor(*args, **traits):
    """ Returns an instance of the toolkit-specific editor factory declared in
    enthought.traits.ui.<toolkit>.rgb_color_editor. If such an editor factory
    cannot be located, an instance of the abstract ToolkitEditorFactory
    declared in enthought.traits.ui.editors.rgb_color_editor is returned.

    Parameters
    ----------
    \*args, \*\*traits
        arguments and keywords to be passed on to the editor
        factory's constructor.
    """

    try:
       return toolkit_object('rgb_color_editor:ToolkitEditorFactory', True)(
                                                            *args, **traits)
    except:
       return ToolkitEditorFactory(*args, **traits)
