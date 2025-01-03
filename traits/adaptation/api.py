# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from .adapter import Adapter, PurePythonAdapter

from .adaptation_error import AdaptationError

from .adaptation_manager import (
    adapt,
    AdaptationManager,
    get_global_adaptation_manager,
    provides_protocol,
    register_factory,
    register_offer,
    register_provides,
    reset_global_adaptation_manager,
    set_global_adaptation_manager,
    supports_protocol,
)

from .adaptation_offer import AdaptationOffer
