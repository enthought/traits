#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   09/01/2005
#
#------------------------------------------------------------------------------

""" Displays a message to the user as a modal window.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import HasPrivateTraits, Str, Float

from .view import View

from .group import HGroup

from .item import Item, spring

from ...pyface.timer.api import do_after

#-------------------------------------------------------------------------------
#  'Message' class:
#-------------------------------------------------------------------------------

class Message ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The message to be displayed
    message = Str

#-------------------------------------------------------------------------------
#  Displays a user specified message:
#-------------------------------------------------------------------------------

def message ( message = '', title = 'Message', buttons = [ 'OK' ],
              parent  = None ):
    """ Displays a message to the user as a model window with the specified
    title and buttons.

    If *buttons* is not specified, a single **OK** button is used, which is
    appropriate for notifications, where no further action or decision on the
    user's part is required.
    """
    msg = Message( message = message )
    ui  = msg.edit_traits( parent = parent,
                           view   = View( [ 'message~', '|<>' ],
                                          title   = title,
                                          buttons = buttons,
                                          kind    = 'modal' ) )
    return ui.result

#-------------------------------------------------------------------------------
#  Displays a user specified error message:
#-------------------------------------------------------------------------------

def error ( message = '', title = 'Message', buttons = [ 'OK', 'Cancel' ],
            parent  = None ):
    """ Displays a message to the user as a modal window with the specified
    title and buttons.

    If *buttons* is not specified, **OK** and **Cancel** buttons are used,
    which is appropriate for confirmations, where the user must decide whether
    to proceed. Be sure to word the message so that it is clear that clicking
    **OK** continues the operation.
    """
    msg = Message( message = message )
    ui  = msg.edit_traits( parent = parent,
                           view   = View( [ 'message~', '|<>' ],
                                          title   = title,
                                          buttons = buttons,
                                          kind    = 'modal' ) )
    return ui.result


#-------------------------------------------------------------------------------
#  'AutoCloseMessage' class:
#-------------------------------------------------------------------------------

class AutoCloseMessage ( HasPrivateTraits ):

    # The message to be shown:
    message = Str( 'Please wait' )

    # The time (in seconds) to show the message:
    time = Float( 2.0 )

    def show ( self, parent = None, title = '' ):
        """ Display the wait message for a limited duration.
        """
        view = View(
            HGroup(
                spring,
                Item( 'message',
                      show_label = False,
                      style      = 'readonly'
                ),
                spring
            ),
            title = title
        )

        do_after( int( 1000.0 * self.time ),
                  self.edit_traits( parent = parent, view = view ).dispose )

#-------------------------------------------------------------------------------
#  Displays a user specified message that closes automatically after a specified
#  time interval:
#-------------------------------------------------------------------------------

def auto_close_message ( message = 'Please wait', time   = 2.0,
                         title   = 'Please wait', parent = None ):
    """ Displays a message to the user as a modal window with no buttons. The
        window closes automatically after a specified time interval (specified
        in seconds).
    """
    msg = AutoCloseMessage( message = message, time = time )
    msg.show( parent = parent, title = title )

