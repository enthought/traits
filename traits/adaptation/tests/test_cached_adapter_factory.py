""" Test the cached adapter factory. """


import sys
import unittest

import traits.adaptation.tests.interface_examples
from traits.adaptation.api import AdaptationManager, CachedAdapterFactory


class TestCachedAdapterFactory(unittest.TestCase):
    """ Test the cached adapter factory. """


    examples = traits.adaptation.tests.interface_examples

    #### 'TestCase' protocol ##################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.adaptation_manager = AdaptationManager()

        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """

        return

    #### Tests #################################################################

    def test_cached_adapters(self):

        ex = self.examples

        factory = CachedAdapterFactory(factory=ex.EditorToIPrintable)

        self.adaptation_manager.register_factory(
            factory       = factory,
            from_protocol = ex.Editor,
            to_protocol   = ex.IPrintable
        )

        editor = ex.Editor()

        adapter_1 = self.adaptation_manager.adapt(editor, ex.IPrintable)
        self.assertIsNotNone(adapter_1)
        self.assertIs(type(adapter_1), ex.EditorToIPrintable)

        adapter_2 = self.adaptation_manager.adapt(editor, ex.IPrintable)
        self.assertIsNotNone(adapter_2)
        self.assertIs(type(adapter_2), ex.EditorToIPrintable)

        self.assertIs(adapter_1, adapter_2)

        del adapter_1
        del adapter_2
        del editor

        self.assert_(factory.is_empty)

        return

    def test_cached_adapters_with_lazy_loaded_factory(self):

        LAZY_EXAMPLES = 'traits.adaptation.tests.lazy_examples'
        if LAZY_EXAMPLES in sys.modules:
            del sys.modules[LAZY_EXAMPLES]

        factory = CachedAdapterFactory(factory=LAZY_EXAMPLES + '.IBarToIFoo')

        self.adaptation_manager.register_factory(
            factory       = factory,
            from_protocol = LAZY_EXAMPLES + '.IBar',
            to_protocol   = LAZY_EXAMPLES + '.IFoo',
        )

        self.assertNotIn(LAZY_EXAMPLES, sys.modules)

        # The *actual* factory is loaded on-demand.
        bogus = factory.factory

        self.assertIn(LAZY_EXAMPLES, sys.modules)

        return


if __name__ == '__main__':
    unittest.main()

#### EOF ######################################################################
