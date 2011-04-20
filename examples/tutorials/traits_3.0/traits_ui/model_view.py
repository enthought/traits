#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(ModelView and Controller Classes)-------------------------------------------
"""
ModelView and Controller Classes
================================

Traits 3.0 introduces two new **Handler** subclasses, **ModelView** and
**Controller**, both of which are intended to help simplify the process of
creating MVC (i.e. Model/View/Controller) based applications.

Both **Controller** and **ModelView** classes add the following new traits to
the **Handler** subclass::

    # The model this handler defines a view and controller for:
    model = Instance( HasTraits )

    # The UIInfo object associated with the controller:
    info = Instance( UIInfo )

The *model* trait provides simple access to the model object associated with
either the **Controller** or **ModelView** class. Normally, the *model* trait
is set in the constructor when a **Controller** or **ModelView** subclass is
created. See the **Example** tab for an example of this.

The *info* trait provides access to the **UIInfo** object associated with the
active user interface view for the handler object. The *info* trait is set
automatically when the handler's object view is created.

So far, the **Controller** and **ModelView** classes are identical. The only
difference between them is in the *context* dictionary each class defines when
it creates it associated user interface.

For a **Controller** subclass, the *context* dictionary contains:

object
    The **Controller**'s *model* object.
controller
    The **Controller** object itself.

For a **ModelView** subclass, the *context* dictionary contains:

object
    The **ModelView** object itself.
model
    The **ModelView**'s *model* object.

The **Controller** class is normally used when implementing a standard MVC-based
design. In this case, the *model* object contains most, if not all, of the data
being viewed, and can be easily referenced in the controller's **View**
definition using unqualified trait names (e.g. *Item( 'name' )*).

The **ModelView** class is useful when creating a variant of the standard
MVC-based design the author likes to refer to as a *model-view*. In this
pattern, the **ModelView** subclass typically reformulates a number of the
traits on its associated *model* object as properties on the **ModelView**
class, usually for the purpose of converting the model's data into a more user
interface friendly format.

So in this design, the **ModelView** class not only supplies the view and
controller, but also, in effect, the model (as a set of properties wrapped
around the original model). Because of this, the **ModelView** context
dictionary specifies itself as the special *object* value, and assigns the
original  model as the *model* value. Again, the main purpose of this is to
allow easy reference to the **ModelView**'s property traits within its **View**
using unqualified trait names.

Other than these somewhat subtle, although useful, distinctions, the
**Controller** and **ModelView** classes are identical, and which class to use
is really a personal preference as much as it is a design decision.

Calling the Constructor
-----------------------

Both the **ModelView** and **Controller** classes have the same constructor
signature::

    ModelView( model = None, **metadata )

    Controller( model = None, **metadata )

So both of the following are valid examples of creating a controller for
a model::

    mv = MyModelView( my_model )

    c = MyController( model = my_model )

An Example
----------

The code portion of this lesson provides a complete example of using a
**ModelView** design. Refer to the lesson on *Delegation Fixes and Improvements*
for an example of a related **Controller** based design.
"""

#--<Imports>--------------------------------------------------------------------

from traits.api import *
from traitsui.api import *
from traitsui.table_column import *

#--[Parent Class]---------------------------------------------------------------

class Parent ( HasTraits ):

    first_name = Str
    last_name  = Str

#--[Child Class]----------------------------------------------------------------

class Child ( HasTraits ):

    mother = Instance( Parent )
    father = Instance( Parent )

    first_name = Str
    last_name  = Delegate( 'father' )

#--[ChildModelView Class]-------------------------------------------------------

class ChildModelView ( ModelView ):

    # Define the 'family' ModelView property that maps the child and its
    # parents into a list of objects that can be viewed as a table:
    family = Property( List )

    # Define a view showing the family as a table:
    view = View(
        Item( 'family',
              show_label = False,
              editor = TableEditor(
                  columns = [ ObjectColumn( name = 'first_name' ),
                              ObjectColumn( name = 'last_name' ) ] ) ),
        resizable = True
    )

    # Implementation of the 'family' property:
    def _get_family ( self ):
        return [ self.model.father, self.model.mother, self.model ]

#--[Example*]-------------------------------------------------------------------

# Create a sample family:
mom = Parent( first_name = 'Julia', last_name = 'Wilson' )
dad = Parent( first_name = 'William', last_name = 'Chase' )
son = Child( mother = mom, father = dad, first_name = 'John' )

# Create the controller for the model:
demo = ChildModelView( model = son )

