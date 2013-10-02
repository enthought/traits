""" Tests for dynamic notifiers with `dispatch='ui'`.

Dynamic notifiers created with the `dispatch='ui'` option dispatch event
notifications on the UI thread. The class handling the dispatch,
`FastUITraitChangeNotifyWrapper`, is a subclass of `TraitChangeNotifyWrapper`.
Most of the functionality of the class is thus already covered by the
`TestDynamicNotifiers` test case, and we only need to test that the
notification really occurs on the UI thread.

At present, `dispatch='ui'` and `dispatch='fast_ui'` have the same effect.

"""

# Preamble: Try importing Qt, and set QT_FOUND to True on success.
try:
    from pyface.util.guisupport import get_app_qt4, start_event_loop_qt4

    # This import is necessary to set the `ui_handler` global variable in
    # `traits.trait_notifiers`, which is responsible for dispatching the events
    # to the UI thread.
    from traitsui.qt4 import toolkit

    qt4_app = get_app_qt4()

except Exception:
    QT_FOUND = False

else:
    QT_FOUND = True


import thread
from threading import Thread
import time

from traits.api import Float, HasTraits
from traits.testing.unittest_tools import unittest

from traits import trait_notifiers


class Foo(HasTraits):
    foo = Float


class TestUINotifiers(unittest.TestCase):
    """ Tests for dynamic notifiers with `dispatch='ui'`. """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.notifications = []

    #### 'TestUINotifiers' protocol ###########################################

    def flush_event_loop(self):
        """ Post and process the Qt events. """
        qt4_app.sendPostedEvents()
        qt4_app.processEvents()

    def on_foo_notifications(self, obj, name, old, new):
        thread_id = thread.get_ident()
        event = (thread_id, (obj, name, old, new))
        self.notifications.append(event)

    #### Tests ################################################################

    def test_notification_from_main_thread(self):
        if not QT_FOUND:
            self.skipTest("Qt event loop not found, UI dispatch not possible.")

        obj = Foo()
        obj.on_trait_change(self.on_foo_notifications, 'foo', dispatch='ui')

        obj.foo = 3
        self.flush_event_loop()

        notifications = self.notifications
        self.assertEqual(len(notifications), 1)

        thread_id, event = notifications[0]
        self.assertEqual(event, (obj, 'foo', 0, 3))

        ui_thread = trait_notifiers.ui_thread
        self.assertEqual(thread_id, ui_thread)


    def test_notification_from_separate_thread(self):
        if not QT_FOUND:
            self.skipTest("Qt event loop not found, UI dispatch not possible.")

        obj = Foo()
        obj.on_trait_change(self.on_foo_notifications, 'foo', dispatch='ui')

        # Set obj.foo to 3 on a separate thread.
        def set_foo_to_3(obj):
            obj.foo = 3

        Thread(target=set_foo_to_3, args=(obj,)).start()

        # Wait for a while to make sure the function has finished.
        time.sleep(0.1)

        self.flush_event_loop()

        notifications = self.notifications
        self.assertEqual(len(notifications), 1)

        thread_id, event = notifications[0]
        self.assertEqual(event, (obj, 'foo', 0, 3))

        ui_thread = trait_notifiers.ui_thread
        self.assertEqual(thread_id, ui_thread)


if __name__ == '__main__':
    unittest.main()
