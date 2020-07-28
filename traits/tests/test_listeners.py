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
Test the 'add_trait_listener', 'remove_trait_listener' interface to the
HasTraits class.

"""

import contextlib
import io
import logging
import sys
import threading
import time
import unittest

from traits.api import HasTraits, Str, Int, Float, Any, Event
from traits.api import push_exception_handler, pop_exception_handler


@contextlib.contextmanager
def captured_stderr():
    """
    Return a context manager that directs all stderr output to a string.

    """
    new_stderr = io.StringIO()
    original_stderr = sys.stderr
    sys.stderr = new_stderr
    try:
        yield new_stderr
    finally:
        sys.stderr = original_stderr


class GenerateEvents(HasTraits):
    name = Str
    age = Int
    weight = Float


events = {}  # dict of events


class ListenEvents(HasTraits):

    #  'GenerateEvents' event interface:
    #  the events are stored in the dict 'events'

    def _name_changed(self, object, name, old, new):
        events["_name_changed"] = (name, old, new)

    def _age_changed(self, object, name, old, new):
        events["_age_changed"] = (name, old, new)

    def _weight_changed(self, object, name, old, new):
        events["_weight_changed"] = (name, old, new)

    def alt_name_changed(self, object, name, old, new):
        events["alt_name_changed"] = (name, old, new)

    def alt_weight_changed(self, object, name, old, new):
        events["alt_weight_changed"] = (name, old, new)


class GenerateFailingEvents(HasTraits):
    name = Str

    def _name_changed(self):
        raise RuntimeError


class TestListeners(unittest.TestCase):
    def test_listeners(self):
        global events

        # FIXME: comparing floats
        ge = GenerateEvents()
        le = ListenEvents()

        # Starting test: No Listeners
        ge.trait_set(name="Joe", age=22, weight=152.0)

        # Adding default listener
        ge.add_trait_listener(le)
        events = {}
        ge.trait_set(name="Mike", age=34, weight=178.0)
        self.assertEqual(
            events,
            {
                "_age_changed": ("age", 22, 34),
                "_weight_changed": ("weight", 152.0, 178.0),
                "_name_changed": ("name", "Joe", "Mike"),
            },
        )

        # Adding alternate listener
        ge.add_trait_listener(le, "alt")
        events = {}
        ge.trait_set(name="Gertrude", age=39, weight=108.0)
        self.assertEqual(
            events,
            {
                "_age_changed": ("age", 34, 39),
                "_name_changed": ("name", "Mike", "Gertrude"),
                "_weight_changed": ("weight", 178.0, 108.0),
                "alt_name_changed": ("name", "Mike", "Gertrude"),
                "alt_weight_changed": ("weight", 178.0, 108.0),
            },
        )

        # Removing default listener
        ge.remove_trait_listener(le)
        events = {}
        ge.trait_set(name="Sally", age=46, weight=118.0)
        self.assertEqual(
            events,
            {
                "alt_name_changed": ("name", "Gertrude", "Sally"),
                "alt_weight_changed": ("weight", 108.0, 118.0),
            },
        )

        # Removing alternate listener
        ge.remove_trait_listener(le, "alt")
        events = {}
        ge.trait_set(name="Ralph", age=29, weight=198.0)
        self.assertEqual(events, {})

    def test_trait_exception_handler_can_access_exception(self):
        """ Tests if trait exception handlers can access the traceback of the
        exception.
        """
        from traits import trait_notifiers

        def _handle_exception(obj, name, old, new):
            self.assertIsNotNone(sys.exc_info()[0])

        ge = GenerateFailingEvents()
        try:
            trait_notifiers.push_exception_handler(
                _handle_exception, reraise_exceptions=False, main=True
            )
            ge.trait_set(name="John Cleese")
        finally:
            trait_notifiers.pop_exception_handler()

    def test_exceptions_logged(self):
        # Check that default exception handling logs the exception.
        ge = GenerateFailingEvents()

        traits_logger = logging.getLogger("traits")

        with self.assertLogs(
                logger=traits_logger, level=logging.ERROR) as log_watcher:
            ge.name = "Terry Jones"

        self.assertEqual(len(log_watcher.records), 1)
        log_record = log_watcher.records[0]

        self.assertIn(
            "Exception occurred in traits notification handler",
            log_record.message,
        )

        _, exc_value, exc_traceback = log_record.exc_info
        self.assertIsInstance(exc_value, RuntimeError)
        self.assertIsNotNone(exc_traceback)


class A(HasTraits):
    exception = Any

    foo = Event

    def foo_changed_handler(self):
        pass


def foo_writer(a, stop_event):
    while not stop_event.is_set():
        try:
            a.foo = True
        except Exception as e:
            a.exception = e


class TestRaceCondition(unittest.TestCase):
    def setUp(self):
        push_exception_handler(
            handler=lambda *args: None, reraise_exceptions=True, main=True
        )

    def tearDown(self):
        pop_exception_handler()

    def test_listener_thread_safety(self):
        # Regression test for GitHub issue #56
        a = A()
        stop_event = threading.Event()

        t = threading.Thread(target=foo_writer, args=(a, stop_event))
        t.start()

        for _ in range(100):
            a.on_trait_change(a.foo_changed_handler, "foo")
            time.sleep(0.0001)  # encourage thread-switch
            a.on_trait_change(a.foo_changed_handler, "foo", remove=True)

        stop_event.set()
        t.join()

        self.assertTrue(a.exception is None)

    def test_listener_deleted_race(self):
        # Regression test for exception that occurred when the listener_deleted
        # method is called after the dispose method on a
        # TraitsChangeNotifyWrapper.
        class SlowListener(HasTraits):
            def handle_age_change(self):
                time.sleep(1.0)

        def worker_thread(event_source, start_event):
            # Wait until the listener is set up on the main thread, then fire
            # the event.
            start_event.wait()
            event_source.age = 11

        def main_thread(event_source, start_event):
            listener = SlowListener()
            event_source.on_trait_change(listener.handle_age_change, "age")
            start_event.set()
            # Allow time to make sure that we're in the middle of handling an
            # event.
            time.sleep(0.5)
            event_source.on_trait_change(
                listener.handle_age_change, "age", remove=True
            )

        # Previously, a ValueError would be raised on the worker thread
        # during (normal refcount-based) garbage collection.  That
        # ValueError is ignored by the Python system, so the only
        # visible effect is the output to stderr.
        with captured_stderr() as s:
            start_event = threading.Event()
            event_source = GenerateEvents(age=10)
            t = threading.Thread(
                target=worker_thread, args=(event_source, start_event)
            )
            t.start()
            main_thread(event_source, start_event)
            t.join()

        self.assertNotIn("Exception", s.getvalue())
