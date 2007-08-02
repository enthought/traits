#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------
""" Defines the base PyQt EditorFactory class and classes the various
styles of editors used in a Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.ui.editor_factory \
    import EditorFactory as UIEditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class EditorFactory ( UIEditorFactory ):
    """ Base class for PyQt editor factories.
    """
