# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the adaptation offers. """

import sys
import unittest

from traits.adaptation.adaptation_offer import AdaptationOffer


class TestAdaptationOffer(unittest.TestCase):
    """ Test the adaptation offers. """

    def test_lazy_loading(self):

        LAZY_EXAMPLES = "traits.adaptation.tests.lazy_examples"
        if LAZY_EXAMPLES in sys.modules:
            del sys.modules[LAZY_EXAMPLES]

        offer = AdaptationOffer(
            factory=(LAZY_EXAMPLES + ".IBarToIFoo"),
            from_protocol=(LAZY_EXAMPLES + ".IBar"),
            to_protocol=(LAZY_EXAMPLES + ".IFoo"),
        )

        self.assertNotIn(LAZY_EXAMPLES, sys.modules)

        factory = offer.factory

        self.assertIn(LAZY_EXAMPLES, sys.modules)

        from traits.adaptation.tests.lazy_examples import IBarToIFoo

        self.assertIs(factory, IBarToIFoo)

        del sys.modules[LAZY_EXAMPLES]

        from_protocol = offer.from_protocol

        from traits.adaptation.tests.lazy_examples import IBar

        self.assertIs(from_protocol, IBar)

        del sys.modules[LAZY_EXAMPLES]

        to_protocol = offer.to_protocol

        from traits.adaptation.tests.lazy_examples import IFoo

        self.assertIs(to_protocol, IFoo)

    def test_adaptation_offer_str_representation(self):
        """ test string representation of the AdaptationOffer class. """

        class Foo:
            pass

        class Bar:
            pass

        adaptation_offer = AdaptationOffer(from_protocol=Foo, to_protocol=Bar)
        desired_repr = "<AdaptationOffer: '{}' -> '{}'>".format(
            adaptation_offer.from_protocol_name,
            adaptation_offer.to_protocol_name
        )
        self.assertEqual(desired_repr, str(adaptation_offer))
        self.assertEqual(desired_repr, repr(adaptation_offer))
