# ------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in /LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Description: <Traits component>
# ------------------------------------------------------------------------------

from __future__ import absolute_import

import unittest
import warnings

from traits.api import HasTraits, Category, Str


class Base(HasTraits):
    y = Str("Base y")
    z = Str("Base z")


class BaseExtra(Category, Base):
    x = Str("BaseExtra x")


class BasePlus(Category, Base):
    p = Str("BasePlus p")


#   z = Str("BasePlus z")    overrides not allowed.


class BasePlusPlus(BasePlus):
    pp = Str("BasePlusPlus pp")


class CategoryTestCase(unittest.TestCase):
    """ Test cases for traits category """

    def setUp(self):
        self.base = Base()
        return

    def test_category_deprecated(self):
        class A(HasTraits):
            a = Str()

        with warnings.catch_warnings(record=True) as warn_msgs:
            warnings.simplefilter("always", DeprecationWarning)

            class B(Category, A):
                b = Str()

        # Expect one warning message, originating from the point where
        # the class is defined.
        self.assertEqual(len(warn_msgs), 1)
        warn_msg = warn_msgs[0]
        self.assertIn("Category class is deprecated", str(warn_msg.message))
        self.assertIn("test_category", warn_msg.filename)

    def test_base_category(self):
        """ Base class with traits """
        self.assertEqual(self.base.y, "Base y", msg="y != 'Base y'")
        self.assertEqual(self.base.z, "Base z", msg="z != 'Base z'")
        return

    def test_extra_extension_category(self):
        """ Base class extended with a category subclass """
        self.assertEqual(self.base.x, "BaseExtra x", msg="x != 'BaseExtra x'")
        return

    def test_plus_extension_category(self):
        """ Base class extended with two category subclasses """
        self.assertEqual(self.base.x, "BaseExtra x", msg="x != 'BaseExtra x'")
        self.assertEqual(self.base.p, "BasePlus p", msg="p != 'BasePlus p'")
        return

    def test_subclass_extension_category(self):
        """ Category subclass does not extend base class.
        This test demonstrates that traits allows subclassing of a category
        class, but that the traits from the subclass are not actually added
        to the base class of the Category.
        Seems like the declaration of the subclass (BasePlusPlus) should fail.
        """
        try:
            self.base.pp
            self.fail(
                msg="base.pp should have thrown AttributeError "
                "as Category subclassing is not supported."
            )
        except AttributeError:
            pass

        BasePlusPlus()
        return

    def test_subclass_instance_category(self):
        """ Category subclass instantiation not supported.
        This test demonstrates that traits allows subclassing of a category
        class, that subclass can be instantiated, but the traits of the parent
        class are not inherited.
        Seems like the declaration of the subclass (BasePlusPlus) should fail.
        """
        bpp = BasePlusPlus()
        self.assertEqual(
            bpp.pp, "BasePlusPlus pp", msg="pp != 'BasePlusPlus pp'"
        )

        try:
            self.assertEqual(bpp.p, "BasePlus p", msg="p != 'BasePlus p'")
            self.fail(
                msg="bpp.p should have thrown SystemError as "
                "instantiating a subclass of a category is not "
                "supported."
            )
        except SystemError:
            pass
        return

    def test_subclasses_dont_modify_category_base_class(self):
        # Regression test for enthought/traits#507.
        self.assertEqual(Category.__class_traits__, {})

        class A(HasTraits):
            a = Str()

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always", DeprecationWarning)

            class B(Category, A):
                b = Str()

            class C(Category, A):
                c = Str()

        self.assertEqual(Category.__class_traits__, {})
