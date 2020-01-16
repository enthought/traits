# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the ABC functionality.
"""
import abc
import unittest
import warnings

from traits.api import ABCHasTraits, ABCMetaHasTraits, HasTraits, Int, Float


class TestNew(unittest.TestCase):
    """ Test that __new__ works correctly.
    """

    def setUp(self):
        self.old_filters = warnings.filters[:]
        warnings.simplefilter("error", DeprecationWarning)

    def tearDown(self):
        warnings.filters[:] = self.old_filters

    def test_new(self):
        # Should not raise DeprecationWarning.
        HasTraits(x=10)


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
        return "foo"

    @property
    def bar(self):
        return "bar"


class FooLike(HasTraits):
    x = Int(10)
    y = Float(20.0)

    def foo(self):
        return "foo"

    @property
    def bar(self):
        return "bar"


AbstractFoo.register(FooLike)


class AbstractBar(abc.ABC):
    pass

    @abc.abstractmethod
    def bar(self):
        raise NotImplementedError()


class TestABC(unittest.TestCase):
    def test_basic_abc(self):
        self.assertRaises(TypeError, AbstractFoo)
        concrete = ConcreteFoo()
        self.assertEqual(concrete.foo(), "foo")
        self.assertEqual(concrete.bar, "bar")
        self.assertEqual(concrete.x, 10)
        self.assertEqual(concrete.y, 20.0)
        self.assertTrue(isinstance(concrete, AbstractFoo))

    def test_registered(self):
        foolike = FooLike()
        self.assertTrue(isinstance(foolike, AbstractFoo))

    def test_post_hoc_mixing(self):
        class TraitedBar(HasTraits, AbstractBar, metaclass=ABCMetaHasTraits):
            x = Int(10)

            def bar(self):
                return "bar"

        traited = TraitedBar()
        self.assertTrue(isinstance(traited, AbstractBar))
        self.assertEqual(traited.x, 10)
