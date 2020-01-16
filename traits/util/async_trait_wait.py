# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import threading


def wait_for_condition(condition, obj, trait, timeout=None):
    """
    Wait until the given condition is true, re-evaluating on trait change.

    This is intended for use in multithreading situations where traits can be
    modified from a different thread than the calling thread.

    Wait until `condition` is satisfied.  Raise a RuntimeError if
    `condition` is not satisfied within the given timeout.

    `condition` is a callback function that will be called with `obj`
    as its single argument.  It should return a boolean indicating
    whether the condition is satisfied or not.

    `timeout` gives the maximum time in seconds to wait for the
    condition to become true.  The default value of `None` indicates
    no timeout.

    (obj, trait) give an object and trait to listen to for indication
    of a possible change: whenever the trait changes, the condition is
    re-evaluated.  The condition will also be evaluated on entering
    this function.

    Note that in cases of unusual timing it's possible for the condition to be
    evaluated one more time *after* the ``wait_for_condition`` call has
    returned.

    """
    condition_satisfied = threading.Event()

    def handler():
        if condition(obj):
            condition_satisfied.set()

    obj.on_trait_change(handler, trait)
    try:
        if condition(obj):
            # Catch case where the condition was satisfied before
            # the on_trait_change handler was active.
            pass
        elif timeout is None:
            # Allow a Ctrl-C to interrupt.  The 0.05 value matches
            # what's used by the standard library's Condition.wait.
            while not condition_satisfied.is_set():
                condition_satisfied.wait(timeout=0.05)
        else:
            condition_satisfied.wait(timeout=timeout)
            if not condition_satisfied.is_set():
                raise RuntimeError("Timed out waiting for condition.")
    finally:
        obj.on_trait_change(handler, trait, remove=True)
