# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tests for __repr__ of the ObserverGraph and the various observers. """

import unittest

# imports needed for 'eval' to work

from traits.observation._dict_item_observer import DictItemObserver  # noqa: F401, E501
from traits.observation._filtered_trait_observer import FilteredTraitObserver  # noqa: F401, E501
from traits.observation._list_item_observer import ListItemObserver  # noqa: F401, E501
from traits.observation._metadata_filter import MetadataFilter  # noqa: F401
from traits.observation._named_trait_observer import NamedTraitObserver  # noqa: F401, E501
from traits.observation._observer_graph import ObserverGraph  # noqa: F401
from traits.observation._set_item_observer import SetItemObserver  # noqa: F401

from traits.observation.api import compile_str


class TestGraphRepr(unittest.TestCase):

    def test_repr_roundtrip(self):
        # General note: the goal here is to have a repr that's friendly for
        # debugging and introspection purposes. Having eval(repr(some_graph))
        # evaluate back to that graph is a nice-to-have that may not be
        # achievable in all cases (for example in cases using user-defined
        # lambdas for filtering), and is not intended to be something that
        # end-users rely on. This test is intended to exercise the various
        # __repr__ methods and make sure that the generated representations
        # don't contain obvious syntax errors (missing parentheses, etc.), and
        # checking `eval(repr(graph)) == graph` is a good way to achieve that.

        # Mini-language strings used to create graphs
        test_expressions = [
            "a",
            "a.items",
            "a.b.c",
            "a:b:c",
            "a,b.c,d:e",
            "+tidy",
        ]

        for expression in test_expressions:
            with self.subTest(expression=expression):
                graphs = compile_str(expression)
                self.assertEqual(eval(repr(graphs)), graphs)
