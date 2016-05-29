#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(__getstate__/__setstate__ Changes and Improvements)------------------------
"""
__getstate__/__setstate__ Changes and Improvements
==================================================

Originally, the **HasTraits** class did not define specific *__getstate__* or
*__setstate__* methods for dealing with *pickling* and *unpickling* of
traits-based objects. However, in the course of developing a number of fairly
large-scale applications using Traits, experience has shown that some traits
specific support in this area would be of benefit to most application
developers.

Accordingly, Traits 3.0 introduces *__getstate__* and *__setstate__* methods
that implement several traits aware serialization and deserialization policies.

The *__getstate__* Method
-------------------------

One of the most frequently occurring requirements for serializing an object is
the ability to control which parts of the object's state are saved, and which
parts are discarded.

One typical approach is to define a *__getstate__* method which makes a copy of
the object's *__dict__* attribute and deletes those items which should not be
saved. While this approach works, there are some drawbacks, especially in cases
where heavy use of subclassing is used.

The **HasTraits** *__getstate__* method uses a somewhat different approach by
providing a generic implementation which implements *policies* that developers
can customize through the use of traits *metadata*, in many cases completely
eliminating the need to override or define a *__getstate__* method in their
application classes.

In particular, the **HasTraits** *__getstate__* method saves the value of all
traits which do not have *transient = True* metadata defined. This policy
allows developers to easily mark which trait values should not be saved simply
by adding *transient = True* metadata to them. Besides avoiding having to
write a *__getstate__* method for their class, this approach also provides
good documentation about the *pickling* behavior of the class.

For example::

    class DataBase(HasTraits):

        # The name of the data base file:
        file_name = File

        # The open file handle used to access the data base:
        file = Any(transient = True)

In this example, the **DataBase** class's *file* trait has been mark as
*transient* because it normally contains an open file handle used to access a
data base. Since file handles typically cannot be pickled and restored, the
file handle should not be saved as part of the object's persistent state.
Normally, the file handle would be re-opened by application code after the
object has been restored from its persisted state.

Predefined *transient* Traits
-----------------------------

The Traits package automatically assigns *transient = True* metadata to a
number of predefined traits, thus avoiding the need to explicitly mark them as
transient yourself.

The predefined traits marked as *transient* are:

- **Constant**.
- **Event**.
- *read-only* or *write-only* **Property** traits.
- The *xxx_* trait for *mapped* traits.
- All *_xxx* traits for classes that subclass **HasPrivateTraits**.

Also, by default, delegated traits are only saved if they have a local value
which overrides the value defined by its delegate. You can set *transient =
True* on the delegate trait if you do not want its value to ever be saved.

Overriding *__getstate__*
-------------------------

In general, you should avoid overriding *__getstate__* in subclasses of
**HasTraits**. Instead, mark traits that should not be pickled with
*transient = True* metadata.

However, in cases where this strategy is insufficient, we recommend
overriding *__getstate__* using the follow pattern to remove items that should
not be persisted::

    def __getstate__(self):
        state = super(XXX, self).__getstate__()

        for key in [ 'foo', 'bar' ]:
            if key in state:
                del state[ key ]

        return state

The *__setstate__* Method
-------------------------

The main difference between the default Python *__setstate__*-like behavior and
the new **HasTraits** class *__setstate__* method is that the **HasTraits**
*__setstate__* method actually *sets* the value of each trait using the values
passed to it via its state dictionary argument instead of simply storing or
copying the state dictionary to its *__dict__* attribute.

While slower, this has the advantage of causing trait change notifications to
be generated, which can be very useful for classes which rely of receiving
notifications in order to ensure that their internal object state remains
consistent and up to date.

Overriding *__setstate__*
-------------------------

For classes which do not want to receive change notifications during
*__setstate__*, it is possible to override *__setstate__* and update the
object's *__dict__* attribute directly.

However, in such cases it is important to either call the *__setstate__* super
method (with an empty state dictionary, for example), or to call the
**HasTraits** class's private *_init_trait_listeners* method directly. This
method has no arguments and does not return a result, but it must be called
during *__setstate__* in order to ensure that all dynamic trait change
notifications managed by traits are correctly initialized for the object.
Failure to call this method may result in lost change notifications.
"""

from traits.api import *
from time import time, sleep
from cPickle import dumps, loads


#--[Session Class]-------------------------------------------------------------
class Session(HasTraits):

    # The name of the session:
    name = Str

    # The time the session was created:
    created = Any(transient=True)

    def _name_changed(self):
        self.created = time()

#--[Example*]------------------------------------------------------------------

# The following shows an example of pickling and unpickling a Session object.
# Unfortunately, it is not possible to successfully pickle objects created as
# part of a tutorial, because of problems with pickling objects derived from
# classes dynamically defined using 'exec'. So just use your imagination on
# this one...

# Create a new session:
session = Session(name='session_1')

# Display its contents:
print 'Session name:', session.name
print 'Session created:', session.created

# # Simulate saving the session to a file/database:
# saved_session = dumps(session)
#
# # Simulate the passage of time (zzzzZZZZ...):
# sleep(1)
#
# # Simulate restoring the session from a file/database:
# restored_session = loads(saved_session)
#
# # Display the restored sessions contents (note that the 'created'
# # time should be different from the original session):
# print 'Restored session name:',    restored_session.name
# print 'Restored session created:', restored_session.created
