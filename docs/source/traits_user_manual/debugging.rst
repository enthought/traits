.. index:: debugging, exceptions, trace trait change events

=========================
Tips for debugging Traits
=========================

.. _debugging-change-handler-error:

Re-raising exceptions in change handlers
========================================

Traits will typically log (instead of raise) exceptions when an exception is
encountered in a trait-change handler (see :ref:`observe-notification`). This
behavior is often preferred in applications, since you usually want to avoid
critical failures in applications. However, when debugging these errors, the
``logging.Logger.exception`` only displays the tip of the traceback. For
example, the following change handler raises an exception:

.. code-block:: python

   from traits.api import HasTraits, Int, observe

   class Curmudgeon(HasTraits):
       number = Int(1)

       @observe("number")
       def number_updated(self, event):
           raise ValueError()

   c = Curmudgeon()
   c.number = 42

The script exits normally. The exception is caught and logged::

   Exception occurred in traits notification handler for event object: TraitChangeEvent(object=<__main__.Curmudgeon object at 0x7fed00525220>, name='number', old=1, new=42)
   Traceback (most recent call last):
    ...
   File "curmudgeon.py", line 8, in number_updated
       raise ValueError()
   ValueError

This logged exception, however, only contains the tip of the traceback. This
makes debugging a bit difficult. You can force exceptions to be re-raised
by calling :func:`~traits.testing.unittest_tools.setup_test`:

.. code-block:: python

   from traits.testing.api import setup_test
   setup_test()

This helper function will cause exceptions from ``observe`` or
``on_trait_change`` to be re-raised. This setting can be reversed by
:func:`~traits.testing.unittest_tools.teardown_test`:

.. code-block:: python

   from traits.testing.api import teardown_test
   teardown_test()

Alternatively, you can modify the exception handling just for
``observe``:

.. code-block:: python

   from traits.observation.api import push_exception_handler
   push_exception_handler(reraise_exceptions=True)

Or just for ``on_trait_change``:

.. code-block:: python

   from traits.api import push_exception_handler
   push_exception_handler(reraise_exceptions=True)

(For example, you could add this to the top of the original code block.)

Re-running the original code example with the exception handler will now raise
the following traceback::

   Traceback (most recent call last):
     File "curmudgeon.py", line 15, in <module>
       c.number = 42
     ...
     File "curmudgeon.py", line 12, in number_updated
       raise ValueError()
   ValueError

Notice that this traceback has information about *where* we changed
``number``.


Tracing Traits Change Events
============================

Occasionally it is necessary to find the chain of event dispatches in traits
classes. To help with debugging, a |record_events| context manager is provided
in mod:`traits.util.event_tracer`. Trait change events taking place inside the
context block will be recorded in a change event container (see example below)
and can be saved to files (a file for each thread) for further inspection.


Example:

.. code-block:: python

    from traits.api import *
    from traits.util.event_tracer import record_events


    class MyModel(HasTraits):

        number = Float(2.0)
        list_of_numbers = List(Float())
        count = Int(0)

        @on_trait_change('number')
        def _add_number_to_list(self, value):
            self.list_of_numbers.append(value)

        @on_trait_change('list_of_numbers[]')
        def _count_items(self):
            self.count = len(self.list_on_numbers)

        def add_to_number(self, value):
            self.number += value


    my_model = MyModel()

    with record_events() as change_event_container:
        my_model.number = 4.7
        my_model.number = 3

    # save files locally
    change_event_container.save_to_directory('./')


Running the above example will write a file named MAinThread.trace in the
local folder. The file contents will be similar to the lines below::

    2014-03-21 14:11:20.779000 -> 'number' changed from 2.0 to 4.7 in 'MyModel'
    2014-03-21 14:11:20.779000     CALLING: '_add_number_to_list' in example.py
    2014-03-21 14:11:20.780000 ---> 'list_of_numbers_items' changed from <undefined> to <traits.trait_handlers.TraitListEvent object at 0x03C85AF0> in 'MyModel'
    2014-03-21 14:11:20.780000       CALLING: 'handle_list_items_special' in C:\Users\itziakos\Projects\traits\traits\traits_listener.py
    2014-03-21 14:11:20.780000 -----> 'list_of_numbers_items' changed from [] to [4.7] in 'MyModel'
    2014-03-21 14:11:20.780000         CALLING: '_count_items' in exampler.py
    2014-03-21 14:11:20.780000 -------> 'trait_added' changed from <undefined> to 'list_on_numbers' in 'MyModel'
    2014-03-21 14:11:20.780000           CALLING: '_trait_added_changed' in C:\Users\itziakos\Projects\traits\traits\has_traits.py
    2014-03-21 14:11:20.780000 <------- EXIT: '_trait_added_changed'
    2014-03-21 14:11:20.780000 <----- EXIT: '_count_items' [EXCEPTION: 'MyModel' object has no attribute 'list_on_numbers']
    2014-03-21 14:11:20.780000 <--- EXIT: 'handle_list_items_special'
    2014-03-21 14:11:20.781000 <- EXIT: '_add_number_to_list'

    2014-03-21 14:11:20.781000 -> 'number' changed from 4.7 to 3.0 in 'MyModel'
    2014-03-21 14:11:20.781000     CALLING: '_add_number_to_list' in example.py
    2014-03-21 14:11:20.781000 ---> 'list_of_numbers_items' changed from <undefined> to <traits.trait_handlers.TraitListEvent object at 0x03C85A30> in 'MyModel'
    2014-03-21 14:11:20.781000       CALLING: 'handle_list_items_special' in C:\Users\itziakos\Projects\traits\traits\traits_listener.py
    2014-03-21 14:11:20.781000 -----> 'list_of_numbers_items' changed from [] to [3.0] in 'MyModel'
    2014-03-21 14:11:20.781000         CALLING: '_count_items' in example.py
    2014-03-21 14:11:20.781000 <----- EXIT: '_count_items' [EXCEPTION: 'MyModel' object has no attribute 'list_on_numbers']
    2014-03-21 14:11:20.782000 <--- EXIT: 'handle_list_items_special'
    2014-03-21 14:11:20.782000 <- EXIT: '_add_number_to_list'


.. |record_events| replace:: :func:`~traits.util.event_tracer.record_events`
