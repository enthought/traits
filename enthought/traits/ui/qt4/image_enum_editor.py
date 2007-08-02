#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------
""" Defines the various image enumeration editors and the image enumeration
editor factory for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enum_editor \
    import ToolkitEditorFactory as EditorFactory

from enthought.traits.api \
    import Module, Type, Unicode

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for image enumeration editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Suffix to add to values to form image names:
    suffix = Unicode

    # Path to use to locate image files:
    path = Unicode

    # Class used to derive the path to the image files:
    klass = Type

    # Module used to derive the path to the image files:
    module = Module
