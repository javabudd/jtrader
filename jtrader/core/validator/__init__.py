from .apo import APOValidator
from .macd import MACDValidator
from .adx import ADXValidator
from .robust import RobustValidator
from .rsi import RSIValidator
from .simple import SimpleValidator
from .ultosc import ULTOSCValidator
from .obv import OBVValidator
from .volume import VolumeValidator

__VALIDATORS__ = [
    APOValidator,
    ULTOSCValidator,
    RobustValidator,
    RSIValidator,
    MACDValidator,
    SimpleValidator,
    VolumeValidator,
    ADXValidator,
    OBVValidator
]

__VALIDATION_MAP__ = {
    'apo': __VALIDATORS__[0],
    'ultosc': __VALIDATORS__[1],
    'robust': __VALIDATORS__[2],
    'rsi': __VALIDATORS__[3],
    'macd': __VALIDATORS__[4],
    'simple': __VALIDATORS__[5],
    'volume': __VALIDATORS__[6],
    'adx': __VALIDATORS__[7],
    'obv': __VALIDATORS__[8],
    'all': __VALIDATORS__
}
