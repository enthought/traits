# ------------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Ioannis Tziakos
#  Date:   05/24/2019
#
# ------------------------------------------------------------------------------
import unittest


from traits.api import (
    HasStrictTraits, Int, List, TraitError, TypedReadOnly, Undefined)


class Dummy(HasStrictTraits):

    value_1 = TypedReadOnly(List(Int))

    value_2 = TypedReadOnly(Int)

    events_1 = List

    events_2 = List

    def _value_2_default(self):
        return 8

    def _value_1_changed(self, old, new):
        self.events_1.append((old, new))

    def _value_2_changed(self, old, new):
        self.events_2.append((old, new))


class TestTypedReadOnly(unittest.TestCase):

    def test_initialization(self):
        # given
        dummy = Dummy()

        # when/then
        self.assertEqual(dummy.events_1, [])
        self.assertEqual(dummy.events_2, [])
        self.assertEqual(dummy.value_1, [])
        self.assertEqual(dummy.value_2, 8)

        # when/then
        dummy.events_2 = []
        with self.assertRaises(TraitError):
            dummy.value_2 = 23
        self.assertEqual(dummy.events_2, [])

    def test_setting_value_at_initialization(self):
        # given
        dummy = Dummy(value_1=[1, 2, 7], value_2=46)

        # when/then
        self.assertEqual(dummy.events_1, [(Undefined, [1, 2, 7])])
        self.assertEqual(dummy.events_2, [(Undefined, 46)])
        self.assertEqual(dummy.value_1, [1, 2, 7])
        self.assertEqual(dummy.value_2, 46)

        # when/then
        dummy.events_2 = []
        with self.assertRaises(TraitError):
            dummy.value_2 = 23
        self.assertEqual(dummy.events_2, [])

        # when/then
        dummy.events_1 = []
        with self.assertRaises(TraitError):
            dummy.value_1 = []
        self.assertEqual(dummy.events_1, [])

    def test_setting_value_after_initialization(self):
        # given
        dummy = Dummy()

        # when
        dummy.value_2 = 23

        # then
        self.assertEqual(dummy.events_2, [(Undefined, 23)])
        self.assertEqual(dummy.events_1, [])
        self.assertEqual(dummy.value_2, 23)

        # when
        dummy.value_1 = [9]

        # then
        self.assertEqual(dummy.events_1, [(Undefined, [9])])
        self.assertEqual(dummy.events_2, [(Undefined, 23)])
        self.assertEqual(dummy.value_1, [9])

        # when/then
        dummy.events_2 = []
        with self.assertRaises(TraitError):
            dummy.value_2 = 23
        self.assertEqual(dummy.events_2, [])

        # when/then
        dummy.events_1 = []
        with self.assertRaises(TraitError):
            dummy.value_1 = []
        self.assertEqual(dummy.events_1, [])

    def test_invalid_value(self):
        # given
        dummy = Dummy()

        # when/then
        with self.assertRaises(TraitError):
            dummy.value_2 = '23'
        self.assertEqual(dummy.events_1, [])
        self.assertEqual(dummy.events_2, [])

        # when/then
        with self.assertRaises(TraitError):
            dummy.value_1 = [2, 'dff']
        self.assertEqual(dummy.events_1, [])
        self.assertEqual(dummy.events_2, [])

    def test_clone(self):
        # given
        dummy = Dummy(value_1=[1, 2, 7], value_2=46)
        dummy.events_1 = []
        dummy.events_2 = []

        # when
        cloned = dummy.clone_traits()

        # then
        self.assertEqual(cloned.events_1, [(Undefined, [1, 2, 7])])
        self.assertEqual(cloned.events_2, [(Undefined, 46)])
        self.assertEqual(cloned.value_1, [1, 2, 7])
        self.assertEqual(cloned.value_2, 46)

        # when/then
        cloned.events_2 = []
        with self.assertRaises(TraitError):
            cloned.value_2 = 23
        self.assertEqual(cloned.events_2, [])

        # when/then
        cloned.events_1 = []
        with self.assertRaises(TraitError):
            cloned.value_1 = []
        self.assertEqual(cloned.events_1, [])
