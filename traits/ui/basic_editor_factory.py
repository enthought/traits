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

""" Defines the BasicEditorFactory class, which allows creating editor
    factories that use the same class for creating all editor styles.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import Any

from .editor_factory import EditorFactory

#-------------------------------------------------------------------------------
#  'BasicEditorFactory' base class:
#-------------------------------------------------------------------------------

class BasicEditorFactory ( EditorFactory ):
    """ Base class for editor factories that use the same class for creating
        all editor styles.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Editor class to be instantiated
    klass = Any

    #---------------------------------------------------------------------------
    #  Property getters.
    #---------------------------------------------------------------------------

    def _get_simple_editor_class ( self ):
        """ Returns the editor class to use for "simple" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def _get_custom_editor_class ( self ):
        """ Returns the editor class to use for "custom" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def _get_text_editor_class ( self ):
        """ Returns the editor class to use for "text" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    def _get_readonly_editor_class ( self ):
        """ Returns the editor class to use for "readonly" style views.
        Overridden to return the value of the 'klass' trait.

        """
        return self.klass

    #---------------------------------------------------------------------------
    #  Allow an instance to be called:
    #---------------------------------------------------------------------------

    def __call__ ( self, *args, **traits ):
        return self.set( **traits )

## EOF ########################################################################

