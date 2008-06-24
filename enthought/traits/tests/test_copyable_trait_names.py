import unittest

from enthought.traits.api import HasTraits, \
    Any, Bool, Delegate, Event, Instance, Property, Str

class Foo(HasTraits):

    a = Any
    b = Bool
    s = Str
    i = Instance(HasTraits)
    e = Event
    d = Delegate( 'i' )

    p = Property

    def _get_p(self):
        return self._p

    def _set_p(self, p):
        self._p = p

    # Read Only Property
    p_ro = Property

    def _get_p_ro(self):
        return id(self)

class TestCopyableTraitNames(unittest.TestCase):
    """ Validate that copyable_trait_names returns the appropriate result.
    """

    def setUp(self):
        foo = Foo()
        self.names = foo.copyable_trait_names()

    def test_events_not_copyable(self):
        self.failIf( 'e' in self.names )

    def test_delegate_not_copyable(self):
        self.failIf( 'd' in self.names )

    def test_read_only_property_not_copyable(self):
        self.failIf( 'p_ro' in self.names )

    def test_any_copyable(self):
        self.failUnless( 'a' in self.names )

    def test_bool_copyable(self):
        self.failUnless( 'b' in self.names )

    def test_str_copyable(self):
        self.failUnless( 's' in self.names )

    def test_instance_copyable(self):
        self.failUnless( 'i' in self.names )

    def test_property_copyable(self):
        self.failUnless( 'p' in self.names )

class TestCopyableTraitNameQueries(unittest.TestCase):

    def setUp(self):
        self.foo = Foo()

    def test_type_query(self):
        names = self.foo.copyable_trait_names(**{
            'type': 'trait'
        })

        self.failUnlessEqual(['a', 'i', 's', 'b'], names)

        names = self.foo.copyable_trait_names(**{
            'type': lambda t: t in ('trait', 'property',)
        })

        self.failUnlessEqual(['a', 'p', 's', 'b', 'i'], names)

    def test_property_query(self):
        names = self.foo.copyable_trait_names(**{
            'property': lambda p: p() and p()[1].__name__ == '_set_p',
        })

        self.assertEquals(['p'], names)

    def test_unmodified_query(self):
        names = self.foo.copyable_trait_names(**{
            'is_trait_type': lambda f: f(Str)
        })

        self.assertEquals(['s'], names)

### EOF
