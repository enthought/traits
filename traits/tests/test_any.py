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

from traits.trait_types import Any


class TestAny(unittest.TestCase):
    def test_deprecated_list_default(self):
        message_pattern = r"a default value of type 'list'.* will be shared"
        with self.assertWarnsRegex(DeprecationWarning, message_pattern):
            Any([])

    def test_deprecated_dict_default(self):
        message_pattern = r"a default value of type 'dict'.* will be shared"
        with self.assertWarnsRegex(DeprecationWarning, message_pattern):
            Any({})
