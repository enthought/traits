from .adapter import Adapter, PurePythonAdapter  # noqa: F401

from .adaptation_error import AdaptationError  # noqa: F401

from .adaptation_manager import (  # noqa: F401
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

from .adaptation_offer import AdaptationOffer  # noqa: F401
