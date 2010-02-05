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
""" Defines a drop editor factory for all traits toolkit backends.
    A drop target editor handles drag and drop operations as a drop
    target.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Any, Bool

from .text_editor import ToolkitEditorFactory as EditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for drop editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Allowable drop objects must be of this class (optional)
    klass = Any

    # Must allowable drop objects be bindings?
    binding = Bool(False)

    # Can the user type into the editor, or is it read only?
    readonly = Bool(True)

# Define the DropEditor class.
DropEditor = ToolkitEditorFactory

### EOF #######################################################################
