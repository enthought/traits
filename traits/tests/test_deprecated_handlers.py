# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

#  Imports

import unittest
import warnings

from traits.api import (
    Any,
    ThisClass,
    TraitDict,
    TraitEnum,
    TraitList,
    TraitTuple,
)

class TestTraitHandlerDeprecatedWarnings(unittest.TestCase):

    def test_this_class_warning(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("error", DeprecationWarning)

            with self.assertRaises(DeprecationWarning) as cm:
                ThisClass()

        self.assertIn("ThisClass", str(cm.exception))

    def test_trait_dict_warning(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("error", DeprecationWarning)

            with self.assertRaises(DeprecationWarning) as cm:
                TraitDict()

        self.assertIn("TraitDict", str(cm.exception))

    def test_trait_enum_warning(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("error", DeprecationWarning)

            with self.assertRaises(DeprecationWarning) as cm:
                TraitEnum([1, 2, 3])

        self.assertIn("TraitEnum", str(cm.exception))

    def test_trait_list_warning(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("error", DeprecationWarning)

            with self.assertRaises(DeprecationWarning) as cm:
                TraitList()

        self.assertIn("TraitList", str(cm.exception))

    def test_trait_tuple_warning(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("error", DeprecationWarning)

            with self.assertRaises(DeprecationWarning) as cm:
                TraitTuple([Any, Any])

        self.assertIn("TraitTuple", str(cm.exception))
