# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import inspect
import unittest

from traits.api import (
    BaseCallable,
    Callable,
    Either,
    HasTraits,
    Str,
    TraitError,
)


def function():
    pass


class Dummy(object):

    def instance_method(self):
        pass


class MyCallable(HasTraits):

    value = Callable()

    callable_or_str = Either(Callable(), Str())


class MyBaseCallable(HasTraits):

    value = BaseCallable


class TestCallable(unittest.TestCase):

    def test_default(self):
        a = MyCallable()
        self.assertIsNone(a.value)

    def test_accepts_lambda(self):
        func = lambda v: v + 1    # noqa: E731
        a = MyCallable(value=func)
        self.assertIs(a.value, func)

    def test_accepts_type(self):
        MyCallable(value=float)

    def test_accepts_method(self):
        dummy = Dummy()
        MyCallable(value=dummy.instance_method)

    def test_accepts_function(self):
        MyCallable(value=function)

    def test_rejects_int(self):
        a = MyCallable()

        with self.assertRaises(TraitError) as exception_context:
            a.value = 1

        self.assertIn(
            "must be a callable value", str(exception_context.exception))

    def test_callable_in_complex_trait(self):
        a = MyCallable()

        self.assertIsNone(a.callable_or_str)

        acceptable_values = [pow, "pow", None, int]
        for value in acceptable_values:
            a.callable_or_str = value
            self.assertEqual(a.callable_or_str, value)

        unacceptable_values = [1.0, 3j, (5, 6, 7)]
        for value in unacceptable_values:
            old_value = a.callable_or_str
            with self.assertRaises(TraitError):
                a.callable_or_str = value
            self.assertEqual(a.callable_or_str, old_value)


class TestBaseCallable(unittest.TestCase):

    def test_override_validate(self):
        """ Verify `BaseCallable` can be subclassed to create new traits.
        """
        class ZeroArgsCallable(BaseCallable):

            def validate(self, object, name, value):
                if callable(value):
                    sig = inspect.signature(value)
                    if len(sig.parameters) == 0:
                        return value

                self.error(object, name, value)

        class Foo(HasTraits):
            value = ZeroArgsCallable

        Foo(value=lambda: 1)

        with self.assertRaises(TraitError):
            Foo(value=lambda x: x)

        with self.assertRaises(TraitError):
            Foo(value=1)

    def test_accepts_function(self):
        MyBaseCallable(value=lambda x: x)

    def test_accepts_method(self):
        MyBaseCallable(value=Dummy.instance_method)

    def test_accepts_type(self):
        MyBaseCallable(value=int)

    def test_accepts_none(self):
        MyBaseCallable(value=None)

    def test_rejects_non_callable(self):
        with self.assertRaises(TraitError):
            MyBaseCallable(value=Dummy())

        with self.assertRaises(TraitError):
            MyBaseCallable(value=1)
