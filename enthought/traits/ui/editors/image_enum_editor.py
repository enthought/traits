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

""" Defines the image enumeration editor factory for all traits user interface
toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

import sys

from os import getcwd

from os.path import join, dirname, exists

from ...api import Module, Type, Unicode, on_trait_change

from .enum_editor import ToolkitEditorFactory as EditorFactory

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for image enumeration editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    # Prefix to add to values to form image names:
    prefix = Unicode

    # Suffix to add to values to form image names:
    suffix = Unicode

    # Path to use to locate image files:
    path = Unicode

    # Class used to derive the path to the image files:
    klass = Type

    # Module used to derive the path to the image files:
    module = Module


    #---------------------------------------------------------------------------
    #  Performs any initialization needed after all constructor traits have
    #  been set:
    #---------------------------------------------------------------------------

    def init ( self ):
        """ Performs any initialization needed after all constructor traits
            have been set.
        """
        super( ToolkitEditorFactory, self ).init()
        self._update_path()

    #---------------------------------------------------------------------------
    #  Handles one of the items defining the path being updated:
    #---------------------------------------------------------------------------

    @on_trait_change( 'path, klass, module' )
    def _update_path ( self ):
        """ Handles one of the items defining the path being updated.
        """
        if self.path != '':
            self._image_path = self.path
        elif self.klass is not None:
            module = self.klass.__module__
            if module == '___main___':
                module = '__main__'
            try:
                self._image_path = join( dirname( sys.modules[ module
                                                        ].__file__ ), 'images' )
            except:
                self._image_path = self.path
                dirs = [ join( dirname( sys.argv[0] ), 'images' ),
                         join( getcwd(), 'images' ) ]
                for d in dirs:
                    if exists( d ):
                        self._image_path = d
                        break
        elif self.module is not None:
            self._image_path = join( dirname( self.module.__file__ ), 'images' )

# Define the ImageEnumEditor class.
ImageEnumEditor = ToolkitEditorFactory

## EOF ########################################################################
