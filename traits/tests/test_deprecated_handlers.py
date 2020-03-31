# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
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
    TraitMap,
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
            "TraitMap": [TraitMap, {}],
            "TraitPrefixList": [TraitPrefixList, "one", "two"],
            "TraitPrefixMap": [TraitPrefixMap, {}],
        }

        for name, handler in handlers.items():
            with self.subTest(handler=name):
                with warnings.catch_warnings(record=True):
                    warnings.simplefilter("error", DeprecationWarning)

                    with self.assertRaises(DeprecationWarning) as cm:
                        args = []
                        if isinstance(handler, list) and len(handler) > 0:
                            args = handler[1:]
                            handler = handler[0]
                        handler(*args)
                self.assertIn(name, str(cm.exception))
