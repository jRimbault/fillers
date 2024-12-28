from .bleach import BLEACH
from .naruto import NARUTO
from .shippuden import SHIPPUDEN
from .show import Season, Show

SHOWS = {key.lower(): value for key, value in vars().items() if isinstance(value, Show)}

__all__ = [BLEACH, NARUTO, SHIPPUDEN, Season, Show, SHOWS]
