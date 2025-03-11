# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Int


class Foo(HasTraits):
    bar = Int(5)

    def __init__(self):
        super().__init__()
        self.add_trait("baz", Int(10))


class TestCloneTraitsDynamic(unittest.TestCase):
    """ Validate that `clone_traits()` grabs dynamically added traits.
    """

    __test__ = True

    def setUp(self):
        super().setUp()
        self.foo = Foo()
        self.foo_clone = self.foo.clone_traits()

    def test_setup(self):
        self.assertIsNot(self.foo_clone.baz, None)
        self.assertIs(self.foo_clone.baz, 10)
        self.assertIn("baz", self.foo_clone.trait_names())
