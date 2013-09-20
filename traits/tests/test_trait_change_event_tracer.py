""" Tests for the trait change event tracer. """
from traits.api import Float, HasTraits, on_trait_change
from traits.testing.unittest_tools import unittest

from traits import trait_notifiers


class Foo(HasTraits):
    """ Test traits class with static and dynamic listeners.

    Changing `baz` triggers a dynamic listeners that modifies `bar`, which
    triggers one dynamic and one static listeners.
    """

    bar = Float
    baz = Float

    def _bar_changed(self):
        pass

    @on_trait_change('bar')
    def _on_bar_change_notification(self):
        pass

    @on_trait_change('baz')
    def _on_baz_change_notification(self):
        self.bar += 1


class TestTraitChangeEventTracer(unittest.TestCase):

    def setUp(self):
        self.trait_change_events = []

    def _collect_events(self, *args):
        self.trait_change_events.append(args)

    def test_events_collection(self):

        # Create the test object and a function listener.
        foo = Foo()

        def _on_foo_baz_changed(obj, name, old, new):
            pass
        foo.on_trait_change(_on_foo_baz_changed, 'baz')

        # Set the event tracer and trigger a cascade of change events.
        trait_notifiers.set_trait_change_event_tracer(self._collect_events)

        foo.baz = 3

        self.assertEqual(len(self.trait_change_events), 4)
        expected_events = [
            (foo, 'baz', 0.0, 3.0, foo._on_baz_change_notification),
            (foo, 'bar', 0.0, 1.0, foo._bar_changed.im_func),
            (foo, 'bar', 0.0, 1.0, foo._on_bar_change_notification),
            (foo, 'baz', 0.0, 3.0, _on_foo_baz_changed),
        ]
        self.assertEqual(self.trait_change_events, expected_events)

        # Deactivate the tracer; it should not be called anymore.
        trait_notifiers.clear_trait_change_event_tracer()
        foo.baz = 23
        self.assertEqual(len(self.trait_change_events), 4)


if __name__ == '__main__':
    unittest.main()
