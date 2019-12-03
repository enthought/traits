# Copyright (c) 2019 by Enthought, Inc.
# All rights reserved.

import os
import shutil
import tempfile
import unittest

import six

from traits.api import HasTraits, Int, TraitError
from traits.testing.optional_dependencies import requires_traitsui


@requires_traitsui
class TestViewElements(unittest.TestCase):
    def setUp(self):
        import traitsui.api

        self.toolkit = traitsui.api.toolkit()

    def tearDown(self):
        del self.toolkit

    def test_view_definition(self):
        from traitsui.api import View

        view = View('count')

        class Model(HasTraits):
            count = Int
            my_view = view

        view_elements = Model.class_trait_view_elements()

        self.assertEqual(view_elements.content, {'my_view': view})

    def test_included_names(self):
        from traitsui.api import Group, Item, View

        item = Item('count', id='item_with_id')
        group = Group(item)
        view = View(Item('count'))

        class Model(HasTraits):
            count = Int
            my_group = Group(item)
            my_view = view

        view_elements = Model.class_trait_view_elements()

        self.assertEqual(
            set(view_elements.content),
            {'my_view', 'my_group', 'item_with_id'}
        )

    def test_duplicate_names(self):
        from traitsui.api import Group, Item, View

        class Model(HasTraits):
            count = Int
            includable = Group(Item('count', id='name_conflict'))
            name_conflict = View(Item('count'))

        with self.assertRaises(TraitError):
            Model.class_trait_view_elements()
