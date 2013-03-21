""" Test the ABC functionality.
"""

from traits.testing.unittest_tools import unittest
import warnings

from ..api import HasTraits


class TestNew(unittest.TestCase):
    """ Test that __new__ works correctly.
    """

    def setUp(self):
        self.old_filters = warnings.filters[:]
        warnings.simplefilter('error', DeprecationWarning)

    def tearDown(self):
        warnings.filters[:] = self.old_filters

    def test_new(self):
        # Should not raise DeprecationWarning.
        HasTraits(x=10)

try:
    import abc

    from ..api import ABCHasTraits, ABCMetaHasTraits, HasTraits, Int, Float

    class AbstractFoo(ABCHasTraits):
        x = Int(10)
        y = Float(20.0)

        @abc.abstractmethod
        def foo(self):
            raise NotImplementedError()

        @abc.abstractproperty
        def bar(self):
            raise NotImplementedError()

    class ConcreteFoo(AbstractFoo):
        def foo(self):
            return 'foo'

        @property
        def bar(self):
            return 'bar'

    class FooLike(HasTraits):
        x = Int(10)
        y = Float(20.0)

        def foo(self):
            return 'foo'

        @property
        def bar(self):
            return 'bar'

    AbstractFoo.register(FooLike)


    class AbstractBar(object):
        __metaclass__ = abc.ABCMeta

        @abc.abstractmethod
        def bar(self):
            raise NotImplementedError()


    class TestABC(unittest.TestCase):
        def test_basic_abc(self):
            self.assertRaises(TypeError, AbstractFoo)
            concrete = ConcreteFoo()
            self.assertEquals(concrete.foo(), 'foo')
            self.assertEquals(concrete.bar, 'bar')
            self.assertEquals(concrete.x, 10)
            self.assertEquals(concrete.y, 20.0)
            self.assertTrue(isinstance(concrete, AbstractFoo))

        def test_registered(self):
            foolike = FooLike()
            self.assertTrue(isinstance(foolike, AbstractFoo))

        def test_post_hoc_mixing(self):
            class TraitedBar(HasTraits, AbstractBar):
                __metaclass__ = ABCMetaHasTraits
                x = Int(10)

                def bar(self):
                    return 'bar'

            traited = TraitedBar()
            self.assertTrue(isinstance(traited, AbstractBar))
            self.assertEquals(traited.x, 10)


except ImportError:
    pass
