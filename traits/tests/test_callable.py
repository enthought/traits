# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from inspect import Signature
import unittest

from traits.api import BaseCallable, Callable, HasTraits, TraitError


def function():
    pass


class Dummy(object):

    def instance_method(self):
        pass


class MyCallable(HasTraits):

    value = Callable()


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


class TestBaseCallable(unittest.TestCase):

    def test_override_validate(self):

        class ZeroArgsCallable(BaseCallable):

            def validate(self, object, name, value):
                if callable(value):
                    sig = Signature.from_callable(value)
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
