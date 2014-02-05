""" Tests for dynamic notifiers with `dispatch='greenlet'`.

Dynamic notifiers created with the `dispatch='ui'` option dispatch event
notifications on the UI thread. The class handling the dispatch,
`FastUITraitChangeNotifyWrapper`, is a subclass of `TraitChangeNotifyWrapper`.
Most of the functionality of the class is thus already covered by the
`TestDynamicNotifiers` test case, and we only need to test that the
notification really occurs on the UI thread.

At present, `dispatch='ui'` and `dispatch='fast_ui'` have the same effect.

"""
import gevent

from traits.api import Float, HasTraits, List
from traits.testing.unittest_tools import unittest, UnittestTools

class Foo(HasTraits):
    foo = Float
    boo = Float


class TestGreenletNotifiers(unittest.TestCase, UnittestTools):
    """ Tests for dynamic notifiers with `dispatch='green'`. """

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.notifications = []

    def on_foo_notifications(self, obj, name, old, new):
        if name == 'foo':
            gevent.sleep(1)
        event =(str(gevent.getcurrent()), (obj, name, old, new))
        self.notifications.append(event)

    #### Tests ################################################################

    def test_notification_gevent(self):

        obj = Foo()
        obj.on_trait_change(
            self.on_foo_notifications, 'foo', dispatch='gevent')
        obj.on_trait_change(
            self.on_foo_notifications, 'boo', dispatch='gevent')

        for i in range(100):
            obj.foo = float(i)
            obj.boo = float(i)
        gevent.wait()
        self.assertEqual(len(self.notifications), 198)


if __name__ == '__main__':
    unittest.main()
