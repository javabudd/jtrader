from .apo import APOValidator
from .macd import MACDValidator
from .robust import RobustValidator
from .rsi import RSIValidator
from .simple import SimpleValidator
from .ultosc import ULTOSCValidator
from .volume import VolumeValidator

__VALIDATORS__ = [
    APOValidator,
    ULTOSCValidator,
    RobustValidator,
    RSIValidator,
    MACDValidator,
    SimpleValidator,
    VolumeValidator
]

__VALIDATION_MAP__ = {
    'apo': __VALIDATORS__[0],
    'ultosc': __VALIDATORS__[1],
    'robust': __VALIDATORS__[2],
    'rsi': __VALIDATORS__[3],
    'macd': __VALIDATORS__[4],
    'simple': __VALIDATORS__[5],
    'volume': __VALIDATORS__[6],
    'all': __VALIDATORS__
}
