import unittest

from traits.api import Any, HasStrictTraits, Str


class TestSpecialEvent(unittest.TestCase):
    """ Test demonstrating special change events using the 'event' metadata.
    """

    def setUp(self):
        self.change_events = []
        self.foo = Foo(test=self)

    def test_events(self):
        self.foo.val = "CHANGE"

        values = ["CHANGE"]
        self.assertEqual(self.change_events, values)

    def test_instance_events(self):
        foo = self.foo
        foo.add_trait("val2", Str(event="the_trait"))
        foo.val2 = "CHANGE2"

        values = ["CHANGE2"]
        self.assertEqual(self.change_events, values)


class Foo(HasStrictTraits):
    val = Str(event="the_trait")
    test = Any(None)

    def _the_trait_changed(self, new):
        if self.test is not None:
            self.test.change_events.append(new)
