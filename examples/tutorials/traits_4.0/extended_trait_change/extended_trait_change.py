#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(on_trait_change Method Enhancements)---------------------------------------
"""
on_trait_change Method Enhancements
===================================

In Traits 3.0, the capabilities of the **HasTraits** class's
*on_trait_change* method has been greatly enhanced with the addition of a new
*extended* trait name syntax for specifying the name of the trait the
notification handler applies to.

Previously, the trait name argument to the *on_trait_change* method could only
be one of the following:

Omitted, None, or 'anytrait'
    The notification handler applies to any trait on the object.

name
    The notification handler applies to the trait on the object called *name*.

[name1, ..., namen]
    The notification handler applies to each of the traits on the object with
    the specified names.

In Traits 3.0, all of these forms are still supported, but now the syntax for
specifying *name* has been expanded to allow a much broader set of traits that
are *reachable* from the object the *on_trait_change* method is applied to.

New *name* Parameter Syntax
---------------------------

In Traits 3.0, the *name* parameter, in addition to being omitted, None or
*anytrait*, can now be a single *xname* or a list of *xname* names, where
an *xname* is an extended name of the form::

    xname2['.'xname2]*

An *xname2* is of the form::

   (xname3 | '['xname3[','xname3]*']) ['*']

An *xname3* is of the form::

     xname | ['+'|'-'][name] | name['?' | ('+'|'-')[name]]

A *name* is any valid Python attribute name. The semantic meaning of this
notation is as follows:

[item, item, ..., item]
    A list which matches any of the specified items. Note that at the topmost
    level, the surrounding square brackets are optional.

name?
    If the current object does not have an attribute called *name*, the
    reference can be ignored. If the '?' character is omitted, the current
    object must have a trait called *name*, otherwise an exception will be
    raised.

prefix+
    Matches any trait on the current object whose name begins with *prefix*.

\+metadata_name
    Matches any trait on the current object having *metadata_name* metadata.

\-metadata_name
    Matches any trait on the current object which does not have *metadata_name*
    metadata.

prefix+metadata_name
    Matches any trait on the current object whose name begins with *prefix* and
    which has *metadata_name* metadata.

prefix-metadata_name
    Matches any trait on the current object whose name begins with *prefix* and
    which does not have *metadata_name* metadata.

\+
    Matches all traits on the current object.

pattern*
    Matches object graphs where *pattern* occurs one or more times (useful for
    setting up listeners on recursive data structures like trees or linked
    lists).

Name Syntax Examples
--------------------

Some examples of valid names and their meaning are as follows:

'foo,bar,baz'
    Listen for trait changes to *object.foo*, *object.bar*, and *object.baz*.

['foo','bar','baz']
    Equivalent to 'foo,bar,baz', but may be more useful in cases where the
    individual items are computed.

'foo.bar.baz'
    Listen for trait changes to *object.foo.bar.baz*.

'foo.[bar,baz]'
    Listen for trait changes to *object.foo.bar* and *object.foo.baz*.

'([left,right]).name'
    Listen for trait changes to the *name* trait of each node of a tree having
    *left* and *right* links to other tree nodes, and where *object* is the
    root node of the tree.

'+dirty'
    Listen for trait changes on any trait in the *object* which has the 'dirty'
    metadata set.

'foo.+dirty'
    Listen for trait changes on any trait in *object.foo* which has the 'dirty'
    metadata set.

'foo.[bar,-dirty]'
    Listen for trait changes on *object.foo.bar* or any trait on *object.foo*
    which does not have 'dirty' metadata set.

Additional Semantic Rules
-------------------------

Note that any of the intermediate (i.e., non-final) links in a pattern can be
traits of type **Instance**, **List** or **Dict**. In the case of **List** and
**Dict** traits, the subsequent portion of the pattern is applied to each item
in the list, or value in the dictionary.

For example, if *self.children* is a list, 'children.name' listens for trait
changes to the *name* trait for each item in the *self.children* list.

Also note that items added to or removed from a list or dictionary in the
pattern will cause the *handler* routine to be invoked as well, since this is
treated as an *implied* change to the item's trait being monitored.

Notification Handler Signatures
-------------------------------

The signature of the *handler* supplied also has an effect on how changes to
intermediate traits are processed. The five valid handler signatures are:

1. handler()
2. handler(new)
3. handler(name,new)
4. handler(object,name,new)
5. handler(object,name,old,new)

For signatures 1, 4 and 5, any change to any element of a path being listened
to invokes the handler with information about the particular element that was
modified (e.g., if the item being  monitored is 'foo.bar.baz', a change to
'bar' will call *handler* with the following information:

object
    object.foo
name
    bar
old
    old value for object.foo.bar
new
    new value for object.foo.bar

If one of the intermediate links is a **List** or **Dict**, the call to
*handler* may report an *_items* changed event. If in the previous
example, *bar* is a **List**, and a new item is added to *bar*, then
the information passed to *handler* would be:

object object.foo name bar_items old **Undefined** new **TraitListEvent**
    whose *added* trait contains the new item added to *bar*.

For signatures 2 and 3, the *handler* does not receive enough information to
discern between a change to the final trait being listened to and a change to
an intermediate link. In this case, the event dispatcher will attempt to map a
change to an intermediate link to its effective change on the final trait.
This only works if all of the intermediate links are single values (such as an
**Instance** or **Any** trait) and not **Lists** or **Dicts**. If the modified
intermediate trait or any subsequent intermediate trait preceding the final
trait is a **List** or **Dict**, then a **TraitError** is raised, since the
effective value for the final trait cannot in general be resolved
unambiguously.

Handler signature 1 also has the special characteristic that if a final trait
is a **List** or **Dict**, it will automatically handle *_items* changed
events for the final trait as well. This can be useful in cases where the
*handler* only needs to know that some aspect of the final trait has been
changed. For all other *handler* signatures, you must explicitly specify the
*xxx_items* trait if you want to be notified of changes to any of the items of
the *xxx* trait.

Backward Compatibility
----------------------

The new extended trait name support in Traits 3.0 has one slight semantic
difference with the pre-Traits 3.0 *on_trait_change* method.

Prior to Traits 3.0, it was necessary to make two separate calls to
*on_trait_change* in order to set up listeners on a **List** or **Dict**
trait's value and the contents of its value, as shown in the following
example::

    class Department(HasTraits):

        employees = List(Employee)

        ...

    a_department.on_trait_change(some_listener, 'employees')
    a_department.on_trait_change(some_listener_items, 'employees_items')

In Traits 3.0, this is still the case if the *some_listener* function has one
or more arguments. However, if it has no arguments, the *on_trait_change*
method will automatically call the function either when the trait's value or
its value's contents change. So in Traits 3.0 it is only necessary to write::

    a_department.on_trait_change(some_listener, 'employees')

if the *some_listener* (and *some_listener_items*) function has no arguments.

The net effect of this difference is that code written prior to Traits 3.0
could set up two listeners (e.g. *some_listener* and *some_listener_items*, as
in the example), and then have *both* methods called when the contents of the
trait are modified if the *some_listener* method takes no arguments. Since no
data is passed to the *some_listener* function, there is probably no harm in
doing this, but it does create unnecessary notification handler calls.

As a result, to avoid creating this unwanted overhead in existing code, the
*on_trait_change* method applies pre-Traits 3.0 semantics to all simple names
passed to it (e.g. 'employees'). If you are writing new code and want to
take advantage of the new Traits 3.0 *on_trait_change* semantics for a simple
trait name, you will need to modify the name to use some recognizable aspect of
the new extended trait name syntax.

For example, either of the following lines would cause *new style* semantics to
be applied to the *employees* trait::

    a_department.on_trait_change(some_listener, ' employees')

    a_department.on_trait_change(some_listener, '[employees]')

A Complete Example
------------------

Refer to the code tabs of this lesson for a complete example using
*on_trait_change* with an extended trait name. In particular, check near the
bottom of the **Example** tab for the code that sets up an extended trait
change notification handler using *on_trait_change*.
"""

from traits.api import *


#--[Employee Class]------------------------------------------------------------
class Employee(HasTraits):

    # The name of the employee:
    name = Str

    # The number of sick days they have taken this year:
    sick_days = Int


#--[Department Class]----------------------------------------------------------
class Department(HasTraits):

    # The name of the department:
    name = Str

    # The employees in the department:
    employees = List(Employee)


#--[Corporation Class]---------------------------------------------------------
class Corporation(HasTraits):

    # The name of the corporation:
    name = Str

    # The departments within the corporation:
    departments = List(Department)


#--[Example*]------------------------------------------------------------------
# Create some sample employees:
millie = Employee(name='Millie', sick_days=2)
ralph = Employee(name='Ralph', sick_days=3)
tom = Employee(name='Tom', sick_days=1)
slick = Employee(name='Slick', sick_days=16)
marcelle = Employee(name='Marcelle', sick_days=7)
reggie = Employee(name='Reggie', sick_days=11)
dave = Employee(name='Dave', sick_days=0)
bob = Employee(name='Bob', sick_days=1)
alphonse = Employee(name='Alphonse', sick_days=5)

# Create some sample departments:
accounting = Department(name='accounting',
                        employees=[millie, ralph, tom])

sales = Department(name='Sales',
                   employees=[slick, marcelle, reggie])

development = Department(name='Development',
                         employees=[dave, bob, alphonse])

# Create a sample corporation:
acme = Corporation(name='Acme, Inc.',
                   departments=[accounting, sales, development])


# Define a corporate 'whistle blower' function:
def sick_again(object, name, old, new):
    print '%s just took sick day number %d for this year!' % (
          object.name, new)

# Set up the function as a listener:
acme.on_trait_change(sick_again, 'departments.employees.sick_days')

# Now let's try it out:
slick.sick_days += 1
reggie.sick_days += 1
