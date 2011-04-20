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

""" A Traits UI editor that wraps a WX calendar panel.
"""

from __future__ import absolute_import

from ...trait_types import Bool, Int, Enum, Str
from ..ui_traits import AView
from ..editor_factory import EditorFactory


class DateEditor(EditorFactory):
    """ Editor factory for date/time editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    #-- ReadonlyEditor traits --------------------------------------------------

    # Message to show when Date is None.
    message = Str('Undefined')

    # The string representation of the date to show.  Uses time.strftime format.
    strftime = Str('%B %d %Y (%a)')

    # An optional view to display when a read-only text editor is clicked:
    view = AView

    #-- CustomEditor traits ----------------------------------------------------

    # Should users be able to pick future dates when using the CustomEditor?
    allow_future = Bool(True)

    # How many months to show at a time.
    months = Int(3)

    # True: Must be a List of Dates.  False: Must be a Date instance.
    multi_select = Bool(False)

    # When a user multi-selects entries and some of those entries are already
    # selected and some are not, what should be the behavior for the seletion?
    # Options::
    #
    #     'toggle'     -- Toggle each day to the opposite of the current state.
    #     'on'         -- Always turn them on.
    #     'off'        -- Always turn them off.
    #     'max_change' -- Change all to same state, with most days changing.
    #                     For example 1 selected and 9 not, then they would
    #                     all get selected.
    #     'min_change' -- Change all to same state, with min days changing.
    #                     For example 1 selected and 9 not, then they would
    #                     all get unselected.
    on_mixed_select = Enum('toggle', 'on', 'off', 'max_change', 'min_change')

    # How much space to put between the individual months.
    padding = Int(5)

    # Does the user have to hold down Shift for the left-click multiselect?
    shift_to_select = Bool(False)
