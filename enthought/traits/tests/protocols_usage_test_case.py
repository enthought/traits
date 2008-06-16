""" Tests for protocols usage. """


# Standard library imports.
import pickle, unittest, weakref

# Enthought library imports.
from enthought.io.api \
    import File

from enthought.traits.api \
    import Any, Bool, HasTraits, Instance, Int, Interface, Str, implements, \
           Adapter, adapts

# Test class.
class Person(HasTraits):
    """ A person! """

    name = Str
    age  = Int


class ProtocolsUsageTestCase(unittest.TestCase):
    """ Tests for protocols usage. """

    ###########################################################################
    # 'TestCase' interface.
    ###########################################################################

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """
                   
        return

    def tearDown(self):
        """ Called immediately after each test method has been called. """
        
        return
    
    ###########################################################################
    # Tests.
    ###########################################################################

    def test_adapts(self):
        """ adapts """

        class IFoo(Interface):
            """ A simple interface. """

            def foo(self):
                """ With a single method. """

                
        class Bar(HasTraits):
            """ A type that *doesn't* implement 'IFoo'. """


        class BarToIFooAdapter(Adapter):
            """ Adapts from Bar to IFoo. """

            adapts(Bar, to=IFoo)

            def foo(self):
                """ An implementation of the single. """

                return 'foo'
            

        b = Bar()

        # Make sure that the Bar instance can be adapted to 'IFoo'.
        self.assertNotEqual(None, IFoo(b))
        self.assertEqual('foo', IFoo(b).foo())

        return

    def test_factory(self):
        """ factory """

        class IInputStream(Interface):
            """ Fake interface for input stream. """

            def get_input_stream(self):
                """ Get an input stream. """


        def factory(obj):
            """ A factory for File to IInputStream adapters. """
            
            if not obj.is_folder:
                adapter = FileToIInputStreamAdapter(adaptee=obj)

            else:
                adapter = None

            return adapter

        
        class FileToIInputStreamAdapter(Adapter):
            """ An adapter from 'File' to 'IInputStream'. """

            adapts(File, to=IInputStream, factory=factory)

            ###################################################################
            # 'IInputStream' interface.
            ###################################################################

            def get_input_stream(self):
                """ Get an input stream. """

                return file(self.adaptee.path, 'r')

        # A file... actually, *this* file ;^)
        f = File('protocols_usage_test_case.py')
        self.assertEqual(True, f.is_file)

        # A folder... actually, the folder that *this* file is in.
        g = File('..')
        self.assertEqual(True, g.is_folder)

        # We should be able to adapt the file to an input stream...
        self.assertNotEqual(None, IInputStream(f, None))

        # ... but not the folder.
        self.assertEqual(None, IInputStream(g, None))

        # Make sure we can use the stream (this reads this module and makes
        # sure that it starts with the right doc string).
        stream = IInputStream(f).get_input_stream()
        self.assert_(stream.read().startswith('"""' + __doc__))
        
        return

    def test_when_expression(self):
        """ when expression """

        class IInputStream(Interface):
            """ Fake interface for input stream. """

            def get_input_stream(self):
                """ Get an input stream. """


        class FileToIInputStreamAdapter(Adapter):
            """ An adapter from 'File' to 'IInputStream'. """

            adapts(File, to=IInputStream, when='not adaptee.is_folder')

            ###################################################################
            # 'IInputStream' interface.
            ###################################################################

            def get_input_stream(self):
                """ Get an input stream. """

                return file(self.adaptee.path, 'r')

        # A file... actually, *this* file ;^)
        f = File('protocols_usage_test_case.py')
        self.assertEqual(True, f.is_file)

        # A folder... actually, the folder that *this* file is in.
        g = File('..')
        self.assertEqual(True, g.is_folder)

        # We should be able to adapt the file to an input stream...
        self.assertNotEqual(None, IInputStream(f, None))

        # ... but not the folder.
        self.assertEqual(None, IInputStream(g, None))

        # Make sure we can use the stream (this reads this module and makes
        # sure that it starts with the right doc string).
        stream = IInputStream(f).get_input_stream()
        self.assert_(stream.read().startswith('"""' + __doc__))
        
        return

    def test_cached(self):
        """ cached """

        class ISaveable(Interface):
            """ Fake interface for saveable. """

            # Is the object 'dirty'?
            dirty = Bool(False)
            
            def save(self, output_stream):
                """ Save the object to an output stream. """


        class HasTraitsToISaveableAdapter(Adapter):
            """ An adapter from 'HasTraits' to 'ISaveable'. """

            adapts(HasTraits, to=ISaveable, cached=True)

            #### 'ISaveable' interface ########################################

            # Is the object 'dirty'?
            dirty = Bool(False)
            
            def save(self, output_stream):
                """ Save the object to an output stream. """

                pickle.dump(self.adaptee, output_stream)
                self.dirty = False

                return
            
            #### Private interface ############################################

            def _adaptee_changed(self, old, new):
                """ Static trait change handler. """

                if old is not None:
                    old.on_trait_change(self._set_dirty, remove=True)

                if new is not None:
                    new.on_trait_change(self._set_dirty)

                self._set_dirty()
                
                return

            def _set_dirty(self):
                """ Sets the dirty flag to True. """
                
                self.dirty = True

                return

        # Create some people!
        fred  = Person(name='fred', age=42)
        wilma = Person(name='wilma', age=35)

        fred_saveable = ISaveable(fred)
        self.assertEqual(True, fred_saveable.dirty)

        wilma_saveable = ISaveable(wilma)
        self.assertEqual(True, wilma_saveable.dirty)

        # Make sure that Fred and Wilma have got their own saveable.
        self.assertNotEqual(id(fred_saveable), id(wilma_saveable))

        # But make sure that their saveable's are cached.
        self.assertEqual(id(ISaveable(fred)), id(fred_saveable))
        self.assertEqual(id(ISaveable(wilma)), id(wilma_saveable))

        # Save Fred and Wilma and make sure that the dirty flag is cleared.
        fred_saveable.save(file('fred.pickle', 'w'))
        self.assertEqual(False, ISaveable(fred).dirty)

        wilma_saveable.save(file('wilma.pickle', 'w'))
        self.assertEqual(False, ISaveable(wilma).dirty)

        # Clean up.
        File('fred.pickle').delete()
        File('wilma.pickle').delete()

        return
    
# Run the unit tests (if invoked from the command line):        
if __name__ == '__main__':
    unittest.main()

