# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Tests for the ReadOnly trait type.

"""
import unittest

from traits.api import (
    HasTraits,
    ReadOnly,
    TraitError,
)


class ObjectWithReadOnlyText(HasTraits):
    """ A dummy object that set the readonly trait in __init__

    There exists such usage in TraitsUI.
    """

    text = ReadOnly()

    def __init__(self, text, **traits):
        self.text = text
        super(ObjectWithReadOnlyText, self).__init__(**traits)


class TestReadOnlyTrait(unittest.TestCase):
    """ Test ReadOnly TraitType. """

    def test_set_readonly_trait_in_init(self):

        obj = ObjectWithReadOnlyText(text="ABC")
        self.assertEqual(obj.text, "ABC")

        with self.assertRaises(TraitError):
            obj.text = "XYZ"

        self.assertEqual(obj.text, "ABC")
