# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This example shows how to set up notifications for changes on an object that
is an item in a list.

Note that when a new list is assigned, the change event is of a different type
compared to when a list is mutated.
"""

from traits.api import HasTraits, Int, List, observe
from traits.observation.api import trait


class Person(HasTraits):

    scores = List(Int)

    @observe("scores")
    def notify_scores_change(self, event):
        print(
            "{event.name} changed from {event.old} to {event.new}. "
            "(Event type: {event.__class__.__name__})".format(event=event)
        )

    @observe(trait("scores", notify=False).list_items())
    def notify_scores_content_change(self, event):
        print(
            "scores added: {event.added}. scores removed: {event.removed} "
            "(Event type: {event.__class__.__name__})".format(event=event)
        )


person = Person(scores=[1, 2])
# print: scores changed from [] to [1, 2]. (Event type: TraitChangeEvent)
person.scores.append(3)
# print: scores added: [3]. scores removed: [] (Event type: ListChangeEvent)
