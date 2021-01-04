# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Tools for having doctest and unittest work together more nicely.

    Eclipse's PyDev plugin will run your unittest files for you very nicely.
    The doctest_for_module function allows you to easily run the doctest for a
    module along side your standard unit tests within Eclipse.
"""

# Standard library imports
import doctest
import unittest


def doctest_for_module(module):
    """ Create a TestCase from a module's doctests that will be run by the
        standard unittest.main().

        Example tests/test_foo.py::

            import unittest

            import foo
            from traits.testing.api import doctest_for_module

            class FooTestCase(unittest.TestCase):
                ...

            class FooDocTest(doctest_for_module(foo)):
                pass

            if __name__ == "__main__":
                # This will run and report both FooTestCase and the doctests in
                # module foo.
                unittest.main()

        Alternatively, you can say::

            FooDocTest = doctest_for_module(foo)

        instead of::

            class FooDocTest(doctest_for_module(foo)):
                pass
    """

    class C(unittest.TestCase):
        def test_dummy(self):
            pass  # Make the test case loader find us

        def run(self, result=None):
            # doctest doesn't like nose.result.TextTestResult objects,
            # so we try to determine if thats what we're dealing
            # with and use its internal result attribute instead
            if hasattr(result, "result"):
                doctest.DocTestSuite(module).run(result.result)
            else:
                doctest.DocTestSuite(module).run(result)

    return C
