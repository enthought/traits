""" Test the adapter factories. """


import sys
import unittest

from apptools.adaptation.adapter_factory_offer import AdapterFactoryOffer


class TestAdapterFactoryOffer(unittest.TestCase):

    def test_lazy_loading(self):

        LAZY_EXAMPLES = 'apptools.adaptation.tests.lazy_examples'
        offer = AdapterFactoryOffer(
            factory       =(LAZY_EXAMPLES + '.IBarToIFoo'),
            from_protocol =(LAZY_EXAMPLES + '.IBar'),
            to_protocol   =(LAZY_EXAMPLES + '.IFoo'),
        )

        self.assertNotIn(LAZY_EXAMPLES, sys.modules)

        factory = offer.factory

        self.assertIn(LAZY_EXAMPLES, sys.modules)

        from apptools.adaptation.tests.lazy_examples import IBarToIFoo
        self.assertIs(factory, IBarToIFoo)


        del sys.modules[LAZY_EXAMPLES]

        from_protocol = offer.from_protocol

        from apptools.adaptation.tests.lazy_examples import IBar
        self.assertIs(from_protocol, IBar)


        del sys.modules[LAZY_EXAMPLES]

        to_protocol = offer.to_protocol

        from apptools.adaptation.tests.lazy_examples import IFoo
        self.assertIs(to_protocol, IFoo)


if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
