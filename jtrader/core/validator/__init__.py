from .apo import APOValidator
from .robust import RobustValidator
from .ultosc import ULTOSCValidator

__VALIDATION_MAP__ = {
    "apo": APOValidator,
    "ultosc": ULTOSCValidator,
    "robust": RobustValidator
}

__VALIDATION_MAP__['all'] = __VALIDATION_MAP__
