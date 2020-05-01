# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# observe_different_events.py --- Example of using observe with post_init
from traits.api import HasTraits, Int, List, observe
from traits.observers.api import trait

class Person(HasTraits):

    scores = List(Int)

    @observe("scores")
    def notify_scores_change(self, event):
        print(
            "{name} changed from {old} to {new}. (Event type: {type_})".format(
                name=event.name,
                old=event.old,
                new=event.new,
                type_=type(event).__name__,
            ))

    @observe(trait("scores", notify=False).list_items())
    def notify_scores_content_change(self, event):
        print(
            "scores added: {added}. scores removed: {removed} "
            "(Event type: {type_})".format(
                added=event.added,
                removed=event.removed,
                type_=type(event).__name__,
            ))

person = Person(scores=[1, 2])
# print: scores changed from [] to [1, 2]. (Event type: TraitObserverEvent)
person.scores.append(3)
# print: scores added: [3]. scores removed: [] (Event type: ListObserverEvent)
