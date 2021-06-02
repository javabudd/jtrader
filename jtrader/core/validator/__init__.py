from .apo import APOValidator
from .robust import RobustValidator
from .rsi import RSIValidator
from .ultosc import ULTOSCValidator

__VALIDATION_MAP__ = {
    'apo': APOValidator,
    'ultosc': ULTOSCValidator,
    'robust': RobustValidator,
    'rsi': RSIValidator
}

__VALIDATION_MAP__['all'] = __VALIDATION_MAP__
