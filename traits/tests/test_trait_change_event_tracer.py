""" Tests for the trait change event tracer. """
from traits.api import Float, HasTraits, on_trait_change
from traits.testing.unittest_tools import unittest

from traits import trait_notifiers


class FuzException(Exception):
    pass


class Foo(HasTraits):
    """ Test traits class with static and dynamic listeners.

    Changing `baz` triggers a dynamic listeners that modifies `bar`, which
    triggers one dynamic and one static listeners.
    """

    bar = Float
    baz = Float
    fuz = Float

    def _bar_changed(self):
        pass

    @on_trait_change('bar')
    def _on_bar_change_notification(self):
        pass

    @on_trait_change('baz')
    def _on_baz_change_notification(self):
        self.bar += 1

    @on_trait_change('fuz')
    def _on_fuz_change_notification(self):
        self.bar += 1
        raise FuzException('method')


class TestChangeEventTracers(unittest.TestCase):

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        self.pre_change_events = []
        self.post_change_events = []
        self.exceptions = []
        trait_notifiers.push_exception_handler(
            lambda obj, name, old, new: None
        )

    def tearDown(self):
        trait_notifiers.pop_exception_handler()

    #### Private protocol #####################################################

    def _collect_pre_notification_events(self, *args):
        self.pre_change_events.append(args)

    def _collect_post_notification_events(self, *args, **kwargs):
        self.post_change_events.append(args)
        self.exceptions.extend(kwargs.values())

    #### Tests ################################################################

    def test_change_event_hooks(self):

        # Create the test object and a function listener.
        foo = Foo()

        def _on_foo_baz_changed(obj, name, old, new):
            pass
        foo.on_trait_change(_on_foo_baz_changed, 'baz')

        # Set the event tracer and trigger a cascade of change events.
        trait_notifiers.set_change_event_tracers(
            pre_tracer=self._collect_pre_notification_events,
            post_tracer=self._collect_post_notification_events)

        foo.baz = 3

        self.assertEqual(len(self.pre_change_events), 4)
        self.assertEqual(len(self.post_change_events), 4)

        expected_pre_events = [
            (foo, 'baz', 0.0, 3.0, foo._on_baz_change_notification),
            (foo, 'bar', 0.0, 1.0, foo._bar_changed.im_func),
            (foo, 'bar', 0.0, 1.0, foo._on_bar_change_notification),
            (foo, 'baz', 0.0, 3.0, _on_foo_baz_changed),
        ]
        self.assertEqual(self.pre_change_events, expected_pre_events)

        expected_post_events = [
            (foo, 'bar', 0.0, 1.0, foo._bar_changed.im_func),
            (foo, 'bar', 0.0, 1.0, foo._on_bar_change_notification),
            (foo, 'baz', 0.0, 3.0, foo._on_baz_change_notification),
            (foo, 'baz', 0.0, 3.0, _on_foo_baz_changed),
        ]
        self.assertEqual(self.post_change_events, expected_post_events)

        self.assertEqual(self.exceptions, [None] * 4)

        # Deactivate the tracer; it should not be called anymore.
        trait_notifiers.clear_change_event_tracers()
        foo.baz = 23
        self.assertEqual(len(self.pre_change_events), 4)
        self.assertEqual(len(self.post_change_events), 4)

    def test_change_event_hooks_after_exception(self):

        # Create the test object and a function listener.
        foo = Foo()

        def _on_foo_fuz_changed(obj, name, old, new):
            raise FuzException('function')
        foo.on_trait_change(_on_foo_fuz_changed, 'fuz')

        # Set the event tracer and trigger a cascade of change events.
        trait_notifiers.set_change_event_tracers(
            pre_tracer=self._collect_pre_notification_events,
            post_tracer=self._collect_post_notification_events)

        foo.fuz = 3

        self.assertEqual(len(self.pre_change_events), 4)
        self.assertEqual(len(self.post_change_events), 4)

        expected_pre_events = [
            (foo, 'fuz', 0.0, 3.0, foo._on_fuz_change_notification),
            (foo, 'bar', 0.0, 1.0, foo._bar_changed.im_func),
            (foo, 'bar', 0.0, 1.0, foo._on_bar_change_notification),
            (foo, 'fuz', 0.0, 3.0, _on_foo_fuz_changed),
        ]
        self.assertEqual(self.pre_change_events, expected_pre_events)

        expected_post_events = [
            (foo, 'bar', 0.0, 1.0, foo._bar_changed.im_func),
            (foo, 'bar', 0.0, 1.0, foo._on_bar_change_notification),
            (foo, 'fuz', 0.0, 3.0, foo._on_fuz_change_notification),
            (foo, 'fuz', 0.0, 3.0, _on_foo_fuz_changed),
        ]
        self.assertEqual(self.post_change_events, expected_post_events)

        self.assertEqual(self.exceptions[:2], [None, None])
        self.assertIsInstance(self.exceptions[2], FuzException)
        self.assertEqual(self.exceptions[2].args, ('method',))
        self.assertIsInstance(self.exceptions[3], FuzException)
        self.assertEqual(self.exceptions[3].args, ('function',))


if __name__ == '__main__':
    unittest.main()
