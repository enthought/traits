#------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

from __future__ import absolute_import

from traits.testing.unittest_tools import unittest

from ..api import HasTraits, Trait, TraitError, TraitHandler
from ..trait_base import strx


# Validation via function
def validator(object, name, value):
    if isinstance(value, basestring):
        # arbitrary rule for testing
        if value.find('fail') < 0:
            return value
        else:
            raise TraitError
    else:
        raise TraitError


# Validation via Handler
class MyHandler(TraitHandler):
    def validate(self, object, name, value):
        #print 'myvalidate "%s" %s' % (value, type(value))
        try:
            value = strx(value)
            if value.find('fail') < 0:
                return value
        except:
            pass
        self.error(object, name, value)

        return

    def info(self):
        msg = "a string not containing the character sequence 'fail'"
        return msg


class Foo(HasTraits):
    s = Trait('', validator)


class Bar(HasTraits):
    s = Trait('', MyHandler())


class StrHandlerCase(unittest.TestCase):

    def test_validator_function(self):
        f = Foo()
        self.assertEqual(f.s, '')

        f.s = 'ok'
        self.assertEqual(f.s, 'ok')

        self.assertRaises(TraitError, setattr, f, 's', 'should fail.')
        self.assertEqual(f.s, 'ok')

        return

    def test_validator_handler(self):
        b = Bar()
        self.assertEqual(b.s, '')

        b.s = 'ok'
        self.assertEqual(b.s, 'ok')

        self.assertRaises(TraitError, setattr, b, 's', 'should fail.')
        self.assertEqual(b.s, 'ok')

        return

### EOF
