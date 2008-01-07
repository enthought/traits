#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought logger package component>
#------------------------------------------------------------------------------


# Standard library imports.
import logging
from traceback import format_exception


# Setup a logger for this module.
logger = logging.getLogger(__name__)


"""
    To catch exceptions with our own code this code needs to be added
    sys.excepthook = custom_excepthook
"""

def custom_excepthook(type, value, traceback):
    """ Pass on the exception to the logging system. """

    msg = 'Custom - Traceback (most recent call last):\n'
    list = format_exception(type, value, traceback)

    msg = "".join(list)

    logger.error(msg)

    return


## EOF ##################################################################
