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
import warnings

from traits.api import (
    TraitDict,
    TraitList,
    TraitPrefixList,
    TraitPrefixMap,
    TraitTuple,
)


class TestTraitHandlerDeprecatedWarnings(unittest.TestCase):

    def test_handler_warning(self):
        handlers = {
            "TraitDict": TraitDict,
            "TraitList": TraitList,
            "TraitTuple": TraitTuple,
            "TraitPrefixList": lambda: TraitPrefixList("one", "two"),
            "TraitPrefixMap": lambda: TraitPrefixMap({}),
        }

        for name, handler_factory in handlers.items():
            with self.subTest(handler=name):
                with warnings.catch_warnings(record=True):
                    warnings.simplefilter("error", DeprecationWarning)

                    with self.assertRaises(DeprecationWarning) as cm:
                        handler_factory()
                self.assertIn(name, str(cm.exception))
