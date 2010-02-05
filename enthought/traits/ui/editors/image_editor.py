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
#  Date:   06/05/2007
#
#-------------------------------------------------------------------------------

""" Traits UI 'display only' image editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ...api import Property

from ..ui_traits import Image

from ..basic_editor_factory import BasicEditorFactory

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'ImageEditor' editor factory class:
#-------------------------------------------------------------------------------

class ImageEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = Property

    # The optional image resource to be displayed by the editor (if not
    # specified, the editor's object value is used as the ImageResource to
    # display):
    image = Image

    def _get_klass(self):
        """ Returns the editor class to be instantiated.
        """
        return toolkit_object('image_editor:_ImageEditor')

#-- EOF -----------------------------------------------------------------------
