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
#
#------------------------------------------------------------------------------

""" Defines the title editor factory for all traits toolkit backends.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..basic_editor_factory import BasicEditorFactory

from ..toolkit import toolkit_object

# Callable which returns the editor to use in the ui.
def title_editor(*args, **traits):
    return toolkit_object('title_editor:_TitleEditor')(*args, **traits)

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
TitleEditor = BasicEditorFactory(klass = title_editor)

### EOF #######################################################################
