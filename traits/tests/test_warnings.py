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

from traits.api import HasTraits
from traits.has_traits import TraitsWarning


class TestTraitWarning(unittest.TestCase):

    def test_shadowing_method(self):
        class_def = """class UserDefinedClass(HasTraits):
                            {} = "some_value"
                    """

        method_names = [method for method in HasTraits.__dict__.keys()]
        for method_name in method_names:
            with self.subTest(method_name):
                if not method_name.startswith("_"):
                    # Ensure that overriding public method
                    # names raises a warning.
                    with self.assertWarns(TraitsWarning):
                        exec(class_def.format(method_name))
                else:
                    # But overriding private method names is allowed.
                    exec(class_def.format(method_name))
