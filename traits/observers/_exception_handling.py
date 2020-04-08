# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# This module provides the push_exception_handler and pop_exception_handler
# for the observers.

import logging
import sys

_trait_logger = logging.getLogger("traits")


def _log_exception(event):
    """ A handler that logs the exception with the given event.

    Parameters
    ----------
    event : object
        An event object emitted by the notification.
    """
    _trait_logger.exception(
        "Exception occurred in traits notification handler "
        "for event object: %r",
        event,
    )


class ObserverExceptionHandler:
    """ State for an exception handler."""

    def __init__(self, handler, reraise_exceptions):
        """
        Parameters
        ----------
        handler : callable(event)
            A callable to handle an event, in the context of
            an exception.
        reraise_exceptions : boolean
            Whether to reraise the exception.
        """
        self.handler = handler
        self.reraise_exceptions = reraise_exceptions


class ObserverExceptionHandlerStack:
    """ A stack of exception handlers."""

    def __init__(self):
        self.handlers = []

    def push_exception_handler(
            self, handler=_log_exception, reraise_exceptions=False):
        """ Push a new exception handler into the stack. Making it the
        current exception handler.

        Parameters
        ----------
        handler : callable(event)
            A callable to handle an event, in the context of
            an exception.
        reraise_exceptions : boolean
            Whether to reraise the exception.
        """
        self.handlers.append(
            ObserverExceptionHandler(
                handler=handler, reraise_exceptions=reraise_exceptions,
            )
        )

    def pop_exception_handler(self):
        """ Pop the current exception handler from the stack.

        Raises
        ------
        IndexError
            If there are no handlers to pop.
        """
        return self.handlers.pop()

    def handle_exception(self, event):
        """ Handles a traits notification exception using the handler last pushed.

        Parameters
        ----------
        event : object
            An event object emitted by the notification.
        """
        _, excp, _ = sys.exc_info()
        try:
            handler_state = self.handlers[-1]
        except IndexError:
            # We will always handle the exceptions with logging
            handler_state = ObserverExceptionHandler(
                handler=_log_exception,
                reraise_exceptions=False,
            )

        handler_state.handler(event)
        if handler_state.reraise_exceptions:
            raise excp


_exception_handler_stack = ObserverExceptionHandlerStack()
push_exception_handler = _exception_handler_stack.push_exception_handler
pop_exception_handler = _exception_handler_stack.pop_exception_handler
handle_exception = _exception_handler_stack.handle_exception
