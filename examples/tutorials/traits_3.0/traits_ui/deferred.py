#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Deferred UI Notifications)--------------------------------------------------
"""
Deferred UI Notifications
=========================

In Traits 3.0, a change has been made to the way that events are handled in the
Traits UI that should improve the performance and responsive of Traits-based
user interfaces in certain important situations.

In particular, changes made to the underlying model being displayed by a Traits
UI are no longer reflected immediately in the user interface, but are instead
queued up to be processed by the UI thread at its first available opportunity.

More precisely, the first time that a user interface related model trait is
modified, an event requesting a user interface update is generated containing
the old and new values of the trait. Subsequent changes to the same model trait
result in no new events being generated, but instead simply update the original
event information with the latest value of the modified trait.

Eventually the UI thread will process the original event, at which point it will
update the user interface using the original old value of the trait along with
the latest new value.

Although this may sound like it should slow down user interface updates, in many
cases where a model is being rapidly updated by calculations running either on a
background or UI thread, it should actually appear to make the system more 
responsive, and should in fact, help prevent or reduce situations where the user 
interface would previously have appeared to be unresponsive due to an excessive 
number of screen updates.
"""

#--<Imports>--------------------------------------------------------------------

from enthought.traits.api import *
from enthought.traits.ui.api import *

#--[Count Class]----------------------------------------------------------------

class Count ( HasTraits ):
    
    count = Int
    go    = Button( 'Count' )
    
    view = View( 
        Item( 'count', style = 'readonly' ),
        Item( 'go', show_label = False )
    )
        
    def _go_changed ( self ):
        # Even though the 'count' trait (which is visible in the UI) is being
        # rapidly updated here, the UI should show only a single update each 
        # time the 'Count' button is clicked. In previous Traits versions, the 
        # user would actually see the counter update sequentially through all 
        # 10,000 values, during which time the user interface would be 
        # unresponsive:
        for i in range( 10000 ):
            self.count += 1
    
#--<Example*>-------------------------------------------------------------------

demo = Count()

