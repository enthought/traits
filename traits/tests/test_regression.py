""" General regression tests for a variety of bugs. """
import gc
import sys

from ..has_traits import HasTraits, Property, on_trait_change
from ..trait_types import Bool, DelegatesTo, Instance, Int
from ..testing.unittest_tools import unittest


class Dummy(HasTraits):
    x = Int(10)


def _create_subclass():
    class Subclass(HasTraits):
        pass
    return Subclass


class Dummy2(HasTraits):
    y = Int(20)
    dummy = Instance(Dummy)


class DelegateMess(HasTraits):
    dummy1 = Instance(Dummy, args=())
    dummy2 = Instance(Dummy2)

    y = DelegatesTo('dummy2')

    handler_called = Bool(False)

    def _dummy2_default(self):
        # Create `self.dummy1`
        return Dummy2(dummy=self.dummy1)

    @on_trait_change('dummy1.x')
    def _on_dummy1_x(self):
        self.handler_called = True

    def _init_trait_listeners(self):
        """ Force the DelegatesTo listener to hook up first to exercise the
        worst case.
        """
        for name in ['y', '_on_dummy1_x']:
            data = self.__class__.__listener_traits__[name]
            getattr(self, '_init_trait_%s_listener' % data[0])(name, *data)


class Presenter(HasTraits):
    obj = Instance(Dummy)
    y = Property(Int(), depends_on='obj.x')

    def _get_y(self):
        return self.obj.x


class TestRegression(unittest.TestCase):

    def test_default_value_for_no_cache(self):
        """ Make sure that CTrait.default_value_for() does not cache the
        result.
        """
        dummy = Dummy()
        # Nothing in the __dict__ yet.
        self.assertEqual(dummy.__dict__, {})
        ctrait = dummy.trait('x')
        default = ctrait.default_value_for(dummy, 'x')
        self.assertEqual(default, 10)
        self.assertEqual(dummy.__dict__, {})

    def test_subclasses_weakref(self):
        """ Make sure that dynamically created subclasses are not held
        strongly by HasTraits.
        """
        previous_subclasses = HasTraits.__subclasses__()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        _create_subclass()
        gc.collect()
        self.assertEqual(previous_subclasses, HasTraits.__subclasses__())

    def test_leaked_property_tuple(self):
        """ the property ctrait constructor shouldn't leak a tuple. """
        class A(HasTraits):
            prop = Property()
        a = A()
        self.assertEqual(sys.getrefcount(a.trait('prop').property()), 1)

    def test_delegate_initializer(self):
        mess = DelegateMess()
        self.assertFalse(mess.handler_called)
        mess.dummy1.x = 20
        self.assertTrue(mess.handler_called)

    def test_no_leaking_notifiers(self):
        """ Extended trait change notifications should not leaf
        TraitChangeNotifyWrappers.
        """
        dummy = Dummy()
        ctrait = dummy._trait('x', 2)
        self.assertEqual(len(ctrait._notifiers(1)), 0)
        presenter = Presenter(obj=dummy)
        self.assertEqual(len(ctrait._notifiers(1)), 1)
        del presenter
        self.assertEqual(len(ctrait._notifiers(1)), 0)

if __name__ == '__main__':
    unittest.main()
