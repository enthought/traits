# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
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

import threading
import time
import unittest

# Preamble: Try importing Qt, and set QT_FOUND to True on success.
try:
    from pyface.util.guisupport import get_app_qt4

    # This import is necessary to set the `ui_handler` global variable in
    # `traits.trait_notifiers`, which is responsible for dispatching the events
    # to the UI thread.
    from traitsui.qt4 import toolkit  # noqa: F401

    qt4_app = get_app_qt4()

except Exception:
    QT_FOUND = False

else:
    QT_FOUND = True


from traits import trait_notifiers
from traits.api import Callable, Float, HasTraits, on_trait_change


class CalledAsMethod(HasTraits):
    foo = Float


class CalledAsDecorator(HasTraits):
    foo = Float

    callback = Callable

    @on_trait_change("foo", dispatch="ui")
    def on_foo_change(self, obj, name, old, new):
        self.callback(obj, name, old, new)


class BaseTestUINotifiers(object):
    """ Tests for dynamic notifiers with `dispatch='ui'`.
    """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.notifications = []

    #### 'TestUINotifiers' protocol ###########################################

    def flush_event_loop(self):
        """ Post and process the Qt events. """
        qt4_app.sendPostedEvents()
        qt4_app.processEvents()

    def on_foo_notifications(self, obj, name, old, new):
        thread_id = threading.current_thread().ident
        event = (thread_id, (obj, name, old, new))
        self.notifications.append(event)

    #### Tests ################################################################

    @unittest.skipIf(
        not QT_FOUND, "Qt event loop not found, UI dispatch not possible."
    )
    def test_notification_from_main_thread(self):

        obj = self.obj_factory()

        obj.foo = 3
        self.flush_event_loop()

        notifications = self.notifications
        self.assertEqual(len(notifications), 1)

        thread_id, event = notifications[0]
        self.assertEqual(event, (obj, "foo", 0, 3))

        ui_thread = trait_notifiers.ui_thread
        self.assertEqual(thread_id, ui_thread)

    @unittest.skipIf(
        not QT_FOUND, "Qt event loop not found, UI dispatch not possible."
    )
    def test_notification_from_separate_thread(self):

        obj = self.obj_factory()

        # Set obj.foo to 3 on a separate thread.
        def set_foo_to_3(obj):
            obj.foo = 3

        threading.Thread(target=set_foo_to_3, args=(obj,)).start()

        # Wait for a while to make sure the function has finished.
        time.sleep(0.1)

        self.flush_event_loop()

        notifications = self.notifications
        self.assertEqual(len(notifications), 1)

        thread_id, event = notifications[0]
        self.assertEqual(event, (obj, "foo", 0, 3))

        ui_thread = trait_notifiers.ui_thread
        self.assertEqual(thread_id, ui_thread)


class TestMethodUINotifiers(BaseTestUINotifiers, unittest.TestCase):
    """ Tests for dynamic notifiers with `dispatch='ui'` set by method call.
    """

    def obj_factory(self):
        obj = CalledAsMethod()
        obj.on_trait_change(self.on_foo_notifications, "foo", dispatch="ui")
        return obj


class TestDecoratorUINotifiers(BaseTestUINotifiers, unittest.TestCase):
    """ Tests for dynamic notifiers with `dispatch='ui'` set by decorator. """

    def obj_factory(self):
        return CalledAsDecorator(callback=self.on_foo_notifications)
