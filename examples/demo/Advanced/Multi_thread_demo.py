#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This demo shows a simple user interface being updated by multiple threads.

When the <b>Start Threads</b> button is pressed, the program starts three
independent threads running. Each thread counts from 0 to 199, updating its
own thread-specific trait, and performs a sleep of a thread-specific duration
between each update.

The <b>Start Threads</b> button is disabled while the threads are running, and
becomes active again once all threads have finished running.
"""

from threading \
    import Thread
    
from time \
    import sleep
    
from enthought.traits.api \
    import HasTraits, Int, Button
    
from enthought.traits.ui.api \
    import View, Item

class ThreadDemo ( HasTraits ):
    
    # The thread specific counters:
    thread_0 = Int
    thread_1 = Int
    thread_2 = Int
    
    # The button used to start the threads running:
    start = Button( 'Start Threads' )
    
    # The count of how many threads ae currently running:
    running = Int
    
    view = View(
        Item( 'thread_0', style = 'readonly' ),
        Item( 'thread_1', style = 'readonly' ),
        Item( 'thread_2', style = 'readonly' ), 
        '_',
        Item( 'start', show_label   = False, 
                       width        = -90,
                       enabled_when = 'running == 0' ),
        resizable = True
    )
    
    def _start_changed ( self ):
        for i in range( 3 ):
            Thread( target = self.counter, 
                    args   = ( 'thread_%d' % i, (i*10 + 10)/1000.0 ) ).start()
            
    def counter ( self, name, interval ):
        self.running += 1
        count = 0
        for i in range( 200 ):
            setattr( self, name, count )
            count += 1
            sleep( interval )
        self.running -= 1
        
# Create the demo:        
demo = ThreadDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
