# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
"""
Test the push_exception_handler and pop_exception_handler for the observers
"""
import io
import unittest
from unittest import mock

from traits.observers._exception_handling import (
    ObserverExceptionHandlerStack,
)


class TestExceptionHandling(unittest.TestCase):

    def test_default_logging(self):
        stack = ObserverExceptionHandlerStack()

        with mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
            try:
                raise ZeroDivisionError()
            except Exception:
                stack.handle_exception("Event")

        content = stderr.getvalue()
        self.assertIn(
            "Exception occurred in traits notification handler for "
            "event object: {!r}".format("Event"),
            content,
        )

    def test_push_exception_handler(self):
        # Test pushing an exception handler
        # with the default logging handler and reraise_exceptions set to True.

        stack = ObserverExceptionHandlerStack()

        stack.push_exception_handler(reraise_exceptions=True)

        with mock.patch("sys.stderr", new_callable=io.StringIO) as stderr, \
                self.assertRaises(ZeroDivisionError):

            try:
                raise ZeroDivisionError()
            except Exception:
                stack.handle_exception("Event")

        content = stderr.getvalue()
        self.assertIn("ZeroDivisionError", content)

    def test_push_exception_handler_collect_events(self):

        events = []

        def handler(event):
            events.append(event)

        stack = ObserverExceptionHandlerStack()
        stack.push_exception_handler(handler=handler)

        try:
            raise ZeroDivisionError()
        except Exception:
            stack.handle_exception("Event")

        self.assertEqual(events, ["Event"])

    def test_pop_exception_handler(self):

        stack = ObserverExceptionHandlerStack()

        stack.push_exception_handler(reraise_exceptions=True)
        stack.pop_exception_handler()

        # This should not raise as we fall back to the default

        with mock.patch("sys.stderr"):
            try:
                raise ZeroDivisionError()
            except Exception:
                stack.handle_exception("Event")
