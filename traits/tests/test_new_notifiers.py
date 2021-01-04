# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for dynamic notifiers with `dispatch='new'`.

Dynamic notifiers created with the `dispatch='new'` option dispatch event
notifications on a new thread. The class handling the dispatch,
`NewTraitChangeNotifyWrapper`, is a subclass of `TraitChangeNotifyWrapper`.
Most of the functionality of the class is thus already covered by the
`TestDynamicNotifiers` test case, and we only need to test that the
notification really occurs on a separate thread.

"""
import threading
import unittest
from unittest import mock

from traits.api import Float, HasTraits, List
from traits.testing.unittest_tools import UnittestTools

# Timeout for blocking calls, in seconds.
SAFETY_TIMEOUT = 10.0


class RememberThreads(object):
    """
    Context manager that behaves like Thread, but remembers created
    threads so that they can be joined.
    """
    def __init__(self):
        self._threads = []

    def __call__(self, *args, **kwargs):
        thread = threading.Thread(*args, **kwargs)
        self._threads.append(thread)
        return thread

    def __enter__(self):
        return self

    def __exit__(self, *exc_args):
        threads = self._threads
        while threads:
            thread = threads.pop()
            # Don't wait forever, but raise if we failed to join.
            thread.join(timeout=SAFETY_TIMEOUT)
            if thread.is_alive():
                raise RuntimeError("Failed to join thread")


class Foo(HasTraits):
    foo = Float


class Receiver(HasTraits):
    notifications = List()

    def notified(self):
        # Have we received any notifications?
        return bool(self.notifications)


class TestNewNotifiers(UnittestTools, unittest.TestCase):
    """ Tests for dynamic notifiers with `dispatch='new'`. """

    def test_notification_on_separate_thread(self):
        receiver = Receiver()

        def on_foo_notifications(obj, name, old, new):
            thread_id = threading.current_thread().ident
            event = (thread_id, obj, name, old, new)
            receiver.notifications.append(event)

        obj = Foo()
        obj.on_trait_change(on_foo_notifications, "foo", dispatch="new")

        with RememberThreads() as remember_threads:
            patcher = mock.patch(
                "traits.trait_notifiers.Thread",
                new=remember_threads
            )
            with patcher:
                obj.foo = 3

            self.assertEventuallyTrue(
                receiver, "notifications_items", Receiver.notified,
                timeout=SAFETY_TIMEOUT)

        notifications = receiver.notifications
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0][1:], (obj, "foo", 0, 3))

        this_thread_id = threading.current_thread().ident
        self.assertNotEqual(this_thread_id, notifications[0][0])
