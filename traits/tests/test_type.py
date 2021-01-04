# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Subclass, TraitError, Type


class BaseClass:
    pass


class DerivedClass(BaseClass):
    pass


class UnrelatedClass:
    """ Does not extend the BaseClass """
    pass


class ExampleTypeModel(HasTraits):
    _class = Type(klass=BaseClass)


class ExampleSubclassModel(HasTraits):
    _class = Subclass(BaseClass)


class TypeTestCase(unittest.TestCase):
    """ Tests the Type trait and its alias - the Subclass trait"""

    def test_type_base(self):
        model = ExampleTypeModel(_class=BaseClass)
        self.assertIsInstance(model._class(), BaseClass)

    def test_type_derived(self):
        model = ExampleTypeModel(_class=DerivedClass)
        self.assertIsInstance(model._class(), DerivedClass)

    def test_invalid_type(self):
        example_model = ExampleTypeModel()

        def assign_invalid():
            example_model._class = UnrelatedClass

        self.assertRaises(TraitError, assign_invalid)

    def test_subclass_base(self):
        model = ExampleSubclassModel(_class=BaseClass)
        self.assertIsInstance(model._class(), BaseClass)

    def test_subclass_derived(self):
        model = ExampleSubclassModel(_class=DerivedClass)
        self.assertIsInstance(model._class(), DerivedClass)

    def test_invalid_subclass(self):
        example_model = ExampleSubclassModel()

        def assign_invalid():
            example_model._class = UnrelatedClass

        self.assertRaises(TraitError, assign_invalid)
