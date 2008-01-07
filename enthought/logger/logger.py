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
""" Convenience functions for creating logging handlers etc. """


# Standard library imports.
import logging
from logging.config import fileConfig
from logging.handlers import RotatingFileHandler
import os

# Enthought library imports.
from enthought.util.api import deprecated

# Local imports.
from null_handler import NullHandler


# The default logging level.
LEVEL = logging.DEBUG

# The default formatter.
FORMATTER = logging.Formatter('%(levelname)s|%(asctime)s|%(message)s')

# Does a logging configuration file exist in the working directory?
CONFIG_FILE_EXISTS = os.path.exists('logging.cfg')


# If a logging configuration file exists then use it!
if CONFIG_FILE_EXISTS:
     fileConfig('logging.cfg')

else:
     logging.getLogger().setLevel(LEVEL)
     
     # fixme: Add a null handler so that people using just the ETS library and
     # not one of our applications won't see the warning about 'no handlers'.
     #
     # fixme: I'm not sure this is really a good idea. Wouldn't we want them to
     # know that we are using logging but they haven't configured a handler?!?
     logging.getLogger().addHandler(NullHandler())


# fixme: This reference to the root logger needs to be removed. Instead,
# modules should use:-
#
# import logging
# logger = logging.getLogger(__name__)
#
# Obviously, this means changing practically every module in the library, so
# we won't remove it just yet ;^)
logger = logging.getLogger()


class LogFileHandler(RotatingFileHandler):
     """ The default log file handler. """

     ##########################################################################
     # 'object' interface. 
     ##########################################################################

     def __init__(self, path, maxBytes=1000000, backupCount=3):
          """ Constructor. """

          RotatingFileHandler.__init__(
               self, path, maxBytes=maxBytes, backupCount=3
           )

          # Set our default formatter and log level.
          self.setFormatter(FORMATTER)
          self.setLevel(LEVEL)

          return

     
@deprecated('use "LogFileHandler"')
def create_log_file_handler(path, maxBytes=1000000, backupCount=3):
     """ Creates a log file handler.

     This is just a convenience function to make it easy to create the same
     kind of handlers across applications.

     It sets the handler's formatter to the default formatter, and its logging
     level to the default logging level.

     """
    
     handler = RotatingFileHandler(
         path, maxBytes=maxBytes, backupCount=backupCount
     )

     handler.setFormatter(FORMATTER)
     handler.setLevel(LEVEL)

     return handler


def add_log_queue_handler(logger):
    """ Adds a queueing log handler to a logger. """

    # fixme: The constructor 'logging.Handler' adds the handler to a list
    # that it tries to clean up at process exit time. This means that you
    # should not create a handler unless you are sure that you are actually
    # going to use it, and since the log queue handler is a singleton (yuk!)
    # created at module load time, we have to do the import here.
    from log_queue_handler import log_queue_handler

    # Add the handler to the root logger.
    log_queue_handler.setLevel(LEVEL)
    log_queue_handler.setFormatter(FORMATTER)
    logging.getLogger().addHandler(log_queue_handler)

    return

#### EOF ######################################################################
