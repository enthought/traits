# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.observers._observer_change_notifier import ObserverChangeNotifier


class TestObserverChangeNotifierCall(unittest.TestCase):

    def test_init_and_call(self):
        path = mock.Mock()
        observer_handler = mock.Mock()
        event_factory = mock.Mock(return_value="Event")
        handler = mock.Mock()
        target = mock.Mock()
        dispatcher = mock.Mock()

        notifier = ObserverChangeNotifier(
            observer_handler=observer_handler,
            path=path,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
            event_factory=event_factory,
        )
        notifier(a=1, b=2)

        event_factory.assert_called_once_with(a=1, b=2)
        observer_handler.assert_called_once_with(
            event="Event",
            path=path,
            handler=handler,
            target=target,
            dispatcher=dispatcher,
        )
