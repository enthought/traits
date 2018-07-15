from traits.api import DelegatesTo, Event, HasTraits, Instance
from traits.testing.unittest_tools import unittest


class Parent(HasTraits):
    button = Event()


class Child(HasTraits):
    parent = Instance(Parent)
    button = DelegatesTo('parent')


class TestDelegatesError(unittest.TestCase):

    def test_delegate_event_raises_attribute_error(self):
        c = Child(parent=Parent())
        with self.assertRaises(AttributeError):
            c.button
