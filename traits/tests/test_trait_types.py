# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Unit test case for testing trait types created by subclassing TraitType.
"""

import os
import sys
import tempfile
import textwrap
import shutil
import subprocess
import unittest

from traits.api import (
    DefaultValue,
    Float,
    Function,
    Method,
    NoDefaultSpecified,
    Symbol,
    TraitType,
    Undefined
)
from traits.testing.optional_dependencies import requires_numpy


class TraitTypesTest(unittest.TestCase):
    def test_traits_shared_transient(self):
        # Regression test for a bug in traits where the same _metadata
        # dictionary was shared between different trait types.
        class LazyProperty(TraitType):

            #: The default value type to use.
            default_value_type = DefaultValue.constant

            def get(self, obj, name):
                return 1729

        self.assertFalse(Float().transient)
        LazyProperty().as_ctrait()
        self.assertFalse(Float().transient)

    @requires_numpy
    def test_numpy_validators_loaded_if_numpy_present(self):
        # If 'numpy' is available, the numpy validators should be loaded,
        # even if numpy is imported after traits.
        test_script = textwrap.dedent("""
            from traits.trait_types import bool_fast_validate
            import numpy

            if numpy.bool_ in bool_fast_validate:
                print("Success")
            else:
                print("Failure")
        """)
        this_python = sys.executable
        tmpdir = tempfile.mkdtemp()
        try:
            tmpfile = os.path.join(tmpdir, "test_script.py")
            with open(tmpfile, "w", encoding="utf-8") as f:
                f.write(test_script)
            cmd = [this_python, tmpfile]
            output = subprocess.check_output(cmd).decode("utf-8")
        finally:
            shutil.rmtree(tmpdir)

        self.assertEqual(output.strip(), "Success")

    def test_default_value_in_init(self):

        class MyTraitType(TraitType):
            pass

        # Tests for the behaviour of the default_value argument
        # to TraitType.__init__.
        trait_type = MyTraitType(default_value=23)
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, 23),
        )

        # An explicit default value of None should work as expected.
        trait_type = MyTraitType(default_value=None)
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, None),
        )

        # If no default is given, get_default_value() returns a value
        # of Undefined.
        trait_type = MyTraitType()
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, Undefined),
        )

        # Similarly, if NoDefaultSpecified is given, get_default_value()
        # is Undefined.
        trait_type = MyTraitType(default_value=NoDefaultSpecified)
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, Undefined),
        )

    def test_disallowed_default_value(self):
        class MyTraitType(TraitType):

            default_value_type = DefaultValue.disallow

        trait_type = MyTraitType()
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.disallow, Undefined)
        )

        ctrait = trait_type.as_ctrait()
        self.assertEqual(
            ctrait.default_value(),
            (DefaultValue.disallow, Undefined),
        )
        self.assertEqual(ctrait.default_kind, "invalid")
        self.assertEqual(ctrait.default, Undefined)

        with self.assertRaises(ValueError):
            ctrait.default_value_for(None, "<dummy>")

    def test_call_sets_default_value_type(self):
        class FooTrait(TraitType):
            default_value_type = DefaultValue.callable_and_args

            def __init__(self, default_value=NoDefaultSpecified, **metadata):
                default_value = (pow, (3, 4), {})
                super().__init__(default_value, **metadata)

        trait = FooTrait()
        ctrait = trait.as_ctrait()
        self.assertEqual(ctrait.default_value_for(None, "dummy"), 81)
        cloned_ctrait = trait(30)
        self.assertEqual(cloned_ctrait.default_value_for(None, "dummy"), 30)


class TestDeprecatedTraitTypes(unittest.TestCase):
    def test_function_deprecated(self):
        def some_function():
            pass

        with self.assertWarnsRegex(DeprecationWarning, "Function trait type"):
            Function()
        with self.assertWarnsRegex(DeprecationWarning, "Function trait type"):
            Function(some_function, washable=True)

    def test_method_deprecated(self):

        class A:
            def some_method(self):
                pass

        with self.assertWarnsRegex(DeprecationWarning, "Method trait type"):
            Method()
        with self.assertWarnsRegex(DeprecationWarning, "Method trait type"):
            Method(A().some_method, gluten_free=False)

    def test_symbol_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning, "Symbol trait type"):
            Symbol("random:random")
