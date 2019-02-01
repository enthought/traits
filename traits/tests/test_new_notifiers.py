""" Tests for dynamic notifiers with `dispatch='new'`.

Dynamic notifiers created with the `dispatch='new'` option dispatch event
notifications on a new thread. The class handling the dispatch,
`NewTraitChangeNotifyWrapper`, is a subclass of `TraitChangeNotifyWrapper`.
Most of the functionality of the class is thus already covered by the
`TestDynamicNotifiers` test case, and we only need to test that the
notification really occurs on a separate thread.

"""
import threading
import time
import unittest

from traits.api import Float, HasTraits


class Foo(HasTraits):
    foo = Float


class TestNewNotifiers(unittest.TestCase):
    """ Tests for dynamic notifiers with `dispatch='new'`. """

    def test_notification_on_separate_thread(self):
        notifications = []

        def on_foo_notifications(obj, name, old, new):
            thread_id = threading.current_thread().ident
            event = (thread_id, obj, name, old, new)
            notifications.append(event)

        obj = Foo()
        obj.on_trait_change(on_foo_notifications, "foo", dispatch="new")

        obj.foo = 3
        # Wait for a while to make sure the notification has finished.
        time.sleep(0.1)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0][1:], (obj, "foo", 0, 3))

        this_thread_id = threading.current_thread().ident
        self.assertNotEqual(this_thread_id, notifications[0][0])
