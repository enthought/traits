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
    ThisClass,
    TraitDict,
    TraitEnum,
    TraitList,
    TraitTuple,
)

class TestTraitHandlerDeprecatedWarnings(unittest.TestCase):

    def test_handler_warning(self):
        handlers = [ThisClass, TraitDict, TraitEnum, TraitList, TraitTuple]

        for handler in handlers:
            with self.subTest(handler=handler):
                with warnings.catch_warnings(record=True):
                    warnings.simplefilter("error", DeprecationWarning)

                    with self.assertRaises(DeprecationWarning) as cm:
                        handler()
                self.assertIn(handler.__name__, str(cm.exception))
