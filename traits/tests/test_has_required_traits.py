# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from traits.api import Int, Float, String, HasRequiredTraits, TraitError


class TestHasRequiredTraits(unittest.TestCase):
    def test_trait_value_assignment(self):
        test_instance = RequiredTest(i_trait=4, f_trait=2.2, s_trait="test")
        self.assertEqual(test_instance.i_trait, 4)
        self.assertEqual(test_instance.f_trait, 2.2)
        self.assertEqual(test_instance.s_trait, "test")
        self.assertEqual(test_instance.non_req_trait, 4.4)
        self.assertEqual(test_instance.normal_trait, 42.0)

    def test_missing_required_trait(self):
        with self.assertRaises(TraitError) as exc:
            RequiredTest(i_trait=3)
        self.assertEqual(
            exc.exception.args[0],
            "The following required traits were not "
            "provided: f_trait, s_trait.",
        )


class RequiredTest(HasRequiredTraits):
    i_trait = Int(required=True)
    f_trait = Float(required=True)
    s_trait = String(required=True)
    non_req_trait = Float(4.4, required=False)
    normal_trait = Float(42.0)
