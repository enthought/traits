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
