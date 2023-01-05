# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Perform timing tests on various trait styles to determine the amount of
overhead that traits add.

"""

from time import time
from ..api import Any, DelegatesTo, HasTraits, Int, Range

# Number of iterations to perform:
n = 1000000

# Loop overhead time (actual value determined first time a measurement is made)
t0 = -1.0


#  Measure how long it takes to execute a specified function:
def measure(func):
    now = time()
    func()
    return time() - now


#  'Old style' Python attribute get/set:
class old_style_value:
    def measure(self, reference_get=1.0, reference_set=1.0):
        global t0
        self.init()

        if t0 < 0.0:
            t0 = measure(self.null)
        t1 = measure(self.do_get)
        t2 = measure(self.do_set)

        scale = 1.0e6 / n
        get_time = max(t1 - t0, 0.0) * scale
        set_time = max(t2 - t0, 0.0) * scale

        return get_time, set_time

    def null(self):
        for i in range(n):
            pass

    def init(self):
        self.value = -1

    def do_set(self):
        for i in range(n):
            self.value = i

    def do_get(self):
        for i in range(n):
            self.value


#  'New style' Python attribute get/set:
class new_style_value(object):
    def measure(self):
        global t0
        self.init()

        if t0 < 0.0:
            t0 = measure(self.null)
        t1 = measure(self.do_get)
        t2 = measure(self.do_set)

        scale = 1.0e6 / n
        get_time = max(t1 - t0, 0.0) * scale
        set_time = max(t2 - t0, 0.0) * scale

        return get_time, set_time

    def null(self):
        for i in range(n):
            pass

    def init(self):
        self.value = -1

    def do_set(self):
        for i in range(n):
            self.value = i

    def do_get(self):
        for i in range(n):
            self.value


#  Python 'property' get/set:
class property_value(new_style_value):
    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    value = property(get_value, set_value)


#  Python 'global' get/set:
class global_value(new_style_value):
    def init(self):
        global gvalue
        gvalue = -1

    def do_set(self):
        global gvalue
        for i in range(n):
            gvalue = i

    def do_get(self):
        global gvalue
        for i in range(n):
            gvalue


#  Trait that can have any value:
class any_value(HasTraits, new_style_value):

    value = Any


#  Trait that can only have 'float' values:
class int_value(any_value):

    value = Int


#  Trait that can only have 'range' values:
class range_value(any_value):

    value = Range(-1, 2000000000)


#  Executes method when float trait is changed:
class change_value(int_value):
    def _value_changed(self, old, new):
        pass


#  Notifies handler when float trait is changed:
class monitor_value(int_value):
    def init(self):
        self.on_trait_change(self.on_value_change, "value")

    def on_value_change(self, object, trait_name, old, new):
        pass


#  Float trait is delegated to another object:
class delegate_value(HasTraits, new_style_value):

    value = DelegatesTo("delegate")
    delegate = Any

    def init(self):
        self.delegate = int_value()


#  Float trait is delegated through one object to another object:
class delegate_2_value(delegate_value):
    def init(self):
        delegate = delegate_value()
        delegate.init()
        self.delegate = delegate


#  Float trait is delegated through two objects to another object:
class delegate_3_value(delegate_value):
    def init(self):
        delegate = delegate_2_value()
        delegate.init()
        self.delegate = delegate


#  Run the timing measurements:
def report(name, get_time, set_time, ref_get_time, ref_set_time):
    """ Return string containing a benchmark report.

    The arguments are the name of the benchmark case, the times to do a 'get'
    or a 'set' operation for that benchmark case in usec, and the
    corresponding times for a reference operation (e.g., getting and
    setting an attribute on a new-style instance.
    """

    template = (
        "{name:^30}: Get {get_time:02.3f} us (x {get_speed_up:02.3f}), "
        "Set {set_time:02.3f} us (x {set_speed_up:02.3f})"
    )

    report = template.format(
        name=name,
        get_time=get_time,
        get_speed_up=ref_get_time / get_time,
        set_time=set_time,
        set_speed_up=ref_set_time / set_time,
    )

    return report


def run_benchmark(klass, ref_get_time, ref_set_time):
    benchmark_name = klass.__name__
    get_time, set_time = klass().measure()
    print(
        report(benchmark_name, get_time, set_time, ref_get_time, ref_set_time)
    )


def main():
    ref_get_time, ref_set_time = new_style_value().measure()

    benchmarks = [
        global_value,
        old_style_value,
        new_style_value,
        property_value,
        any_value,
        int_value,
        range_value,
        change_value,
        monitor_value,
        delegate_value,
        delegate_2_value,
        delegate_3_value,
    ]

    for benchmark in benchmarks:
        run_benchmark(benchmark, ref_get_time, ref_set_time)


if __name__ == "__main__":
    main()
