#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#
#------------------------------------------------------------------------------
""" Defines the editor factory for single-selection enumerations, for all traits
    user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

import os, sys

from ..editor_factory import EditorWithListFactory

from ...api import Any, Range, Enum, Bool

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Supported display modes for a custom style editor
Mode = Enum( 'radio', 'list' )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorWithListFactory ):
    """ Editor factory for enumeration editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # (Optional) Function used to evaluate text input:
    evaluate = Any

    # Is user input set on every keystroke (when text input is allowed)?
    auto_set = Bool( True )

    # Number of columns to use when displayed as a grid:
    cols = Range( 1, 20 )

    # Display modes supported for a custom style editor:
    mode = Mode

    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def _get_custom_editor_class ( self ):
        """ Returns the editor class to use for "custom" style views.
        Overridden to return the editor class for the specified mode.
        """
        editor_file_name = \
            os.path.basename(sys.modules[self.__class__.__module__].
                            __file__)
        try:
            if self.mode == 'radio':
                return toolkit_object(editor_file_name.split('.')[0] +
                                      ':RadioEditor',
                                      raise_exceptions = True)
            else:
                return toolkit_object(editor_file_name.split('.')[0] +
                                      ':ListEditor',
                                      raise_exceptions = True)
        except:
            return super(ToolkitEditorFactory, self)._get_custom_editor_class()


# Define the EnumEditor class.
EnumEditor = ToolkitEditorFactory

### EOF #######################################################################
