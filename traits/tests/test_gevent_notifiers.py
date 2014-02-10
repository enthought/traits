""" Tests for dynamic notifiers with `dispatch='gevent'`.

Dynamic notifiers created with the `dispatch='gevent'` option dispatch event
notifications on the gevent event loop. The class handling the dispatch,
`GEventTraitChangeNotifyWrapper`, is a subclass of `TraitChangeNotifyWrapper`.
Most of the functionality of the class is thus already covered by the
`TestDynamicNotifiers` test case, and we only need to test that the
notification really occurs on the gevent eventloop.

At present, `dispatch='ui'` and `dispatch='fast_ui'` have the same effect.

"""
import gevent

from traits.api import Float, HasTraits, List
from traits.testing.unittest_tools import unittest, UnittestTools


class Foo(HasTraits):
    foo = Float
    boo = Float


class TestGEventNotifiers(unittest.TestCase, UnittestTools):
    """ Tests for dynamic notifiers with `dispatch='green'`. """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.notifications = []
        self.greenlets = set()

    def on_foo_notifications(self, obj, name, old, new):
        if name == 'foo':
            gevent.sleep(1)
        event = (obj, name, old, new)
        self.greenlets.add(gevent.getcurrent())
        self.notifications.append(event)

    #### Tests ################################################################

    def test_notification_gevent(self):

        obj = Foo()
        obj.on_trait_change(
            self.on_foo_notifications, 'foo', dispatch='gevent')
        obj.on_trait_change(
            self.on_foo_notifications, 'boo', dispatch='gevent')

        # Events are dispatched into the gevent event loop.
        for i in range(10):
            obj.foo = float(i)
            obj.boo = float(i)
        gevent.wait()

        # Each event should be a separate greenlet
        self.assertEqual(len(self.greenlets), 18)

        # Event should arrive out of order when some of the listeners
        # release the thread.
        self.assertEqual(len(self.notifications), 18)
        previous = None
        for _, name, _, _ in self.notifications:
            if previous is None:
                previous = name
            elif previous == name:
                break
        else:
            self.fail(
                " We should have had some events out of order. "
                " Since half of them are sleeping for 1 second. ")


if __name__ == '__main__':
    unittest.main()
