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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the font editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..editor_factory import EditorFactory

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------
class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for font editors.
    """
    pass


# Define the FontEditor class
# The function will try to return the toolkit-specific editor factory (located
# in enthought.traits.ui.<toolkit>.font_editor, and if none is found, the
# ToolkitEditorFactory declared here is returned.
def FontEditor(*args, **traits):
    """ Returns an instance of the toolkit-specific editor factory declared in
    enthought.traits.ui.<toolkit>.font_editor. If such an editor factory
    cannot be located, an instance of the abstract ToolkitEditorFactory
    declared in enthought.traits.ui.editors.font_editor is returned.

    Parameters
    ----------
    \*args, \*\*traits
        arguments and keywords to be passed on to the editor
        factory's constructor.
    """

    try:
       return toolkit_object('font_editor:ToolkitEditorFactory', True)(*args,
                                                                    **traits)
    except Exception, e:
       return ToolkitEditorFactory(*args, **traits)


## EOF ########################################################################
