# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
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


_logger = logging.getLogger("traits")


class ObserverExceptionHandler:
    """ State for an exception handler.

    Parameters
    ----------
    handler : callable(event) or None
        A callable to handle an event, in the context of
        an exception. If None, the exceptions will be logged.
    reraise_exceptions : boolean
        Whether to reraise the exception.
    """

    def __init__(self, handler, reraise_exceptions):
        self.handler = handler if handler is not None else self._log_exception
        self.reraise_exceptions = reraise_exceptions

    def _log_exception(self, event):
        """ A handler that logs the exception with the given event.

        Parameters
        ----------
        event : object
            An event object emitted by the notification.
        """
        _logger.exception(
            "Exception occurred in traits notification handler "
            "for event object: %r",
            event,
        )


class ObserverExceptionHandlerStack:
    """ A stack of exception handlers.

    Parameters
    ----------
    handlers : list of ObserverExceptionHandler
        The last item is the current handler.
    """

    def __init__(self):
        self.handlers = []

    def push_exception_handler(
            self, handler=None, reraise_exceptions=False):
        """ Push a new exception handler into the stack. Making it the
        current exception handler.

        Parameters
        ----------
        handler : callable(event) or None
            A callable to handle an event, in the context of
            an exception. If None, the exceptions will be logged.
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
            handler_state = ObserverExceptionHandler(
                handler=None,
                reraise_exceptions=False,
            )

        handler_state.handler(event)
        if handler_state.reraise_exceptions:
            raise excp


_exception_handler_stack = ObserverExceptionHandlerStack()
push_exception_handler = _exception_handler_stack.push_exception_handler
pop_exception_handler = _exception_handler_stack.pop_exception_handler
handle_exception = _exception_handler_stack.handle_exception
