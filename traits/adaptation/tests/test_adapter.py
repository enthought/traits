# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the Adapter class. """


import unittest

from traits.api import on_trait_change
from traits.adaptation.api import Adapter


class TestAdapter(unittest.TestCase):
    """ Test the Adapter class. """

    #### Tests ################################################################

    def test_initializing_adaptee(self):
        # Regression test: The `adaptee` trait used to be initialized after
        # all other traits, which caused "post_init" listeners to be
        # incorrectly triggered.

        class FooAdapter(Adapter):
            # True if a trait change notification for `adaptee` is fired.
            adaptee_notifier_called = False
            # True if a  post-init trait change notification for `adaptee`
            # is fired.
            post_init_notifier_called = False

            @on_trait_change("adaptee", post_init=True)
            def check_that_adaptee_start_can_be_accessed(self):
                self.post_init_notifier_called = True

            @on_trait_change("adaptee")
            def check_that_adaptee_change_is_notified(self):
                self.adaptee_notifier_called = True

        foo_adapter = FooAdapter(adaptee="1234")
        self.assertEqual(foo_adapter.adaptee_notifier_called, True)
        self.assertEqual(foo_adapter.post_init_notifier_called, False)
