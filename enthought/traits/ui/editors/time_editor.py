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
#  Author: Judah De Paula
#  Date:   10/7/2008
#
#------------------------------------------------------------------------------

""" A Traits UI editor that wraps a WX timer control.
"""

from __future__ import absolute_import

from ...api import Str
from ..editor_factory import EditorFactory
from ..ui_traits import AView


class TimeEditor(EditorFactory):
    """ Editor factory for time editors.  Generates _TimeEditor()s.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    #-- ReadonlyEditor traits --------------------------------------------------

    # Message to show when Time is None.
    message = Str('Undefined')

    # The string representation of the time to show.  Uses time.strftime format.
    strftime = Str('%I:%M:%S %p')

    # An optional view to display when a read-only text editor is clicked:
    view = AView
