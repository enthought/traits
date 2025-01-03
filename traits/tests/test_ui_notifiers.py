# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for dynamic notifiers with `dispatch='ui'`.

Dynamic notifiers created with the `dispatch='ui'` option dispatch event
notifications on the UI thread. The class handling the dispatch,
`FastUITraitChangeNotifyWrapper`, is a subclass of `TraitChangeNotifyWrapper`.
Most of the functionality of the class is thus already covered by the
`TestDynamicNotifiers` test case, and we only need to test that the
notification really occurs on the UI thread.

At present, `dispatch='ui'` and `dispatch='fast_ui'` have the same effect.
"""

import asyncio
import contextlib
import threading
import unittest

from traits.api import (
    Callable,
    Float,
    get_ui_handler,
    HasTraits,
    on_trait_change,
    set_ui_handler,
)
from traits import trait_notifiers


class CalledAsMethod(HasTraits):
    foo = Float


class CalledAsDecorator(HasTraits):
    foo = Float

    callback = Callable

    @on_trait_change("foo", dispatch="ui")
    def on_foo_change(self, obj, name, old, new):
        self.callback(obj, name, old, new)


def asyncio_ui_handler(event_loop):
    """
    Create a UI handler that dispatches to the asyncio event loop.
    """

    def ui_handler(handler, *args, **kwargs):
        """
        UI handler that dispatches to the asyncio event loop.
        """
        event_loop.call_soon_threadsafe(lambda: handler(*args, **kwargs))

    return ui_handler


@contextlib.contextmanager
def use_asyncio_ui_handler(event_loop):
    """
    Context manager that temporarily sets the UI handler to an asyncio handler.
    """
    old_handler = get_ui_handler()
    set_ui_handler(asyncio_ui_handler(event_loop))
    try:
        yield
    finally:
        set_ui_handler(old_handler)


@contextlib.contextmanager
def clear_ui_handler():
    """
    Context manager that temporarily clears the UI handler.
    """
    old_handler = get_ui_handler()
    set_ui_handler(None)
    try:
        yield
    finally:
        set_ui_handler(old_handler)


class BaseTestUINotifiers(object):
    """Tests for dynamic notifiers with `dispatch='ui'`."""

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.notifications = []
        self.exceptions = []
        self.done = asyncio.Event()
        self.obj = self.obj_factory()

    def enterContext(self, cm):
        # Backport of Python 3.11's TestCase.enterContext method.
        result = type(cm).__enter__(cm)
        self.addCleanup(type(cm).__exit__, cm, None, None, None)
        return result

    #### 'TestUINotifiers' protocol ###########################################

    def modify_obj(self):
        trait_notifiers.push_exception_handler(
            lambda *args: None, reraise_exceptions=True
        )
        try:
            self.obj.foo = 3
        except Exception as e:
            self.exceptions.append(e)
        finally:
            trait_notifiers.pop_exception_handler()

    def on_foo_notifications(self, obj, name, old, new):
        event = (threading.current_thread(), (obj, name, old, new))
        self.notifications.append(event)
        self.done.set()

    #### Tests ################################################################

    def test_notification_from_main_thread_with_no_ui_handler(self):
        # Given
        self.enterContext(clear_ui_handler())

        # When we set obj.foo to 3 on the main thread.
        self.modify_obj()

        # Then the notification is processed synchronously on the main thread.
        self.assertEqual(
            self.notifications,
            [(threading.main_thread(), (self.obj, "foo", 0, 3))],
        )

    def test_notification_from_main_thread_with_registered_ui_handler(self):
        # Given
        self.enterContext(use_asyncio_ui_handler(asyncio.get_event_loop()))

        # When we set obj.foo to 3 on the main thread.
        self.modify_obj()

        # Then the notification is processed synchronously on the main thread.
        self.assertEqual(
            self.notifications,
            [(threading.main_thread(), (self.obj, "foo", 0, 3))],
        )

    def test_notification_from_separate_thread_failure_case(self):
        # Given no registered ui handler
        self.enterContext(clear_ui_handler())

        # When we set obj.foo to 3 on a separate thread, and wait for
        # that thread to complete.
        background_thread = threading.Thread(target=self.modify_obj)
        background_thread.start()
        background_thread.join()

        # Then no notification is processed ...
        self.assertEqual(self.notifications, [])

        # ... and an error was raised
        self.assertEqual(len(self.exceptions), 1)
        self.assertIsInstance(self.exceptions[0], RuntimeError)
        self.assertIn("no UI handler registered", str(self.exceptions[0]))

        # ... but the attribute change was still applied.
        self.assertEqual(self.obj.foo, 3)

    async def test_notification_from_separate_thread(self):
        # Given an asyncio ui handler
        self.enterContext(use_asyncio_ui_handler(asyncio.get_event_loop()))

        # When we set obj.foo to 3 on a separate thread.
        background_thread = threading.Thread(target=self.modify_obj)
        background_thread.start()
        self.addCleanup(background_thread.join)

        # Then the notification will eventually be processed on the main
        # thread.
        await asyncio.wait_for(self.done.wait(), timeout=5.0)
        self.assertEqual(
            self.notifications,
            [(threading.main_thread(), (self.obj, "foo", 0, 3))],
        )
        self.assertEqual(self.obj.foo, 3)


class TestMethodUINotifiers(
    BaseTestUINotifiers, unittest.IsolatedAsyncioTestCase
):
    """Tests for dynamic notifiers with `dispatch='ui'` set by method call."""

    def obj_factory(self):
        obj = CalledAsMethod()
        obj.on_trait_change(self.on_foo_notifications, "foo", dispatch="ui")
        return obj


class TestDecoratorUINotifiers(
    BaseTestUINotifiers, unittest.IsolatedAsyncioTestCase
):
    """Tests for dynamic notifiers with `dispatch='ui'` set by decorator."""

    def obj_factory(self):
        return CalledAsDecorator(callback=self.on_foo_notifications)
