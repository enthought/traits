# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the "Any" trait type.
"""

import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Any


class TestAny(unittest.TestCase):
    def test_list_default(self):
        message_pattern = r"a default value of type 'list'.* will be shared"
        with self.assertWarnsRegex(DeprecationWarning, message_pattern):
            class A(HasTraits):
                foo = Any([])

        # Test the current (but deprecated) copying behaviour
        a = A()
        b = A()
        self.assertEqual(a.foo, [])
        self.assertEqual(b.foo, [])

        a.foo.append(35)
        self.assertEqual(a.foo, [35])
        self.assertEqual(b.foo, [])

    def test_dict_default(self):
        message_pattern = r"a default value of type 'dict'.* will be shared"
        with self.assertWarnsRegex(DeprecationWarning, message_pattern):
            class A(HasTraits):
                foo = Any({})

        # Test the current (but deprecated) copying behaviour
        a = A()
        b = A()
        self.assertEqual(a.foo, {})
        self.assertEqual(b.foo, {})

        a.foo["color"] = "red"
        self.assertEqual(a.foo, {"color": "red"})
        self.assertEqual(b.foo, {})
