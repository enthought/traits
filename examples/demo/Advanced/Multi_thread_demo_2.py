#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo shows a simple user interface being updated by a dynamic number of
threads.

When the <b>Create Threads</b> button is pressed, the <b>count</b> method is 
dispatched on a new thread. It then creates a new <b>Counter</b> object and 
adds it to the <b>counters</b> list (which causes the <b>Counter</b> to appear
in the user interface. It then counts by incrementing the <b>Counter</b>
object's <b>count</b> trait (which again causes a user interface update each
time the counter is incremented). After it reaches its maximum count, it
removes the <b>Counter</b> from the <b>counter</b> list (causing the counter
to be removed from the user interface) and exits (terminating the thread).

Note that repeated clicking of the <b>Create Thread</b> button will create 
additional threads.
"""
    
from time \
    import sleep
    
from enthought.traits.api \
    import HasTraits, Int, Button, List
    
from enthought.traits.ui.api \
    import View, Item, ListEditor
    
#-- The Counter objects used to keep track of the current count ----------------

class Counter ( HasTraits ):

    # The current count:
    count = Int    
    
    view = View( Item( 'count', style = 'readonly' ) )

#-- The main 'ThreadDemo' class ------------------------------------------------

class ThreadDemo ( HasTraits ):
    
    # The button used to start a new thread running:
    create = Button( 'Create Thread' )
    
    # The set of counter objects currently running:
    counters = List( Counter )
    
    view = View(
        Item( 'create', show_label = False, width = -100 ),
        '_',
        Item( 'counters', style      = 'custom',
                          show_label = False,
                          editor     = ListEditor( use_notebook = True,
                                                   dock_style   = 'tab' ) ),
        resizable=True
    )
    
    def __init__ ( self, **traits ):
        super( HasTraits, self ).__init__( **traits )
        
        # Set up the notification handler for the 'Create Thread' button so 
        # that it is run on a new thread:
        self.on_trait_change( self.count, 'create', dispatch = 'new' )
        
    def count ( self ):
        """ This method is dispatched on a new thread each time the 
            'Create Thread' button is pressed.
        """
        counter = Counter()
        self.counters.append( counter )
        for i in range( 1000 ):
            counter.count += 1
            sleep( 0.030 )
        self.counters.remove( counter )
              
# Create the demo:              
demo = ThreadDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
