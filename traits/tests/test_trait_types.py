# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
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
    NoDefaultSpecified,
    Method,
    TraitType,
    Undefined
)
from traits.testing.optional_dependencies import requires_numpy


class TraitTypesTest(unittest.TestCase):
    def test_traits_shared_transient(self):
        # Regression test for a bug in traits where the same _metadata
        # dictionary was shared between different trait types.
        class LazyProperty(TraitType):
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
            from traits.trait_types import float_fast_validate
            import numpy

            if numpy.floating in float_fast_validate:
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
        # Tests for the behaviour of the default_value argument
        # to TraitType.__init__.
        trait_type = TraitType(default_value=23)
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, 23),
        )

        # An explicit default value of None should work as expected.
        trait_type = TraitType(default_value=None)
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, None),
        )

        # If no default is given, get_default_value() returns a value
        # of Undefined.
        trait_type = TraitType()
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, Undefined),
        )

        # Similarly, if NoDefaultSpecified is given, get_default_value()
        # is Undefined.
        trait_type = TraitType(default_value=NoDefaultSpecified)
        self.assertEqual(
            trait_type.get_default_value(),
            (DefaultValue.constant, Undefined),
        )


class TestDeprecatedTraitTypes(unittest.TestCase):
    def test_function_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning, "Function trait type"):
            Function()

    def test_method_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning, "Method trait type"):
            Method()
