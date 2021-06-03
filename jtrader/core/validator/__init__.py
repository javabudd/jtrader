from .apo import APOValidator
from .robust import RobustValidator
from .rsi import RSIValidator
from .ultosc import ULTOSCValidator

__VALIDATORS__ = [
    APOValidator,
    ULTOSCValidator,
    RobustValidator,
    RSIValidator
]

__VALIDATION_MAP__ = {
    'apo': __VALIDATORS__[0],
    'ultosc': __VALIDATORS__[1],
    'robust': __VALIDATORS__[2],
    'rsi': __VALIDATORS__[3],
    'all': __VALIDATORS__
}
