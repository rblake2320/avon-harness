"""Brand registry — single lookup point for all configured brands."""
from .base import BrandConfig
from .avon import AVON
from .mary_kay import MARY_KAY

BRANDS: dict[str, BrandConfig] = {
    "avon": AVON,
    "mary_kay": MARY_KAY,
    # "tupperware": ...,
    # "pampered_chef": ...,
}

_DEFAULT = AVON


def get_brand(name: str) -> BrandConfig:
    """Return BrandConfig for name; falls back to default if unknown."""
    return BRANDS.get(name, _DEFAULT)
