.. index:: debugging, trace trait change events

============================
Tracing Traits Change Events
============================

Occasionally it is necessary to find the chain of event dispatches in traits
classes. To help with debugging a |record_events| context manager is provided
in mod:`traits.util.event_tracer`. Trait change events taking place inside the
context block will be recorded in a change event container (see example below)
and can be saved to files (a file for each thread) for further inspection.


Example::

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


.. |record_events| replace:: :fun:`~traits.util.event_tracer.record_events`
