from .adx import ADXValidator
from .apo import APOValidator
from .macd import MACDValidator
from .obv import OBVValidator
from .pairs import PairsValidator
from .rsi import RSIValidator
from .ultosc import ULTOSCValidator
from .volume import VolumeValidator

__VALIDATORS__ = [
    APOValidator,
    ULTOSCValidator,
    RSIValidator,
    MACDValidator,
    VolumeValidator,
    ADXValidator,
    OBVValidator,
    PairsValidator
]

__VALIDATION_MAP__ = {
    'apo': __VALIDATORS__[0],
    'ultosc': __VALIDATORS__[1],
    'rsi': __VALIDATORS__[2],
    'macd': __VALIDATORS__[3],
    'volume': __VALIDATORS__[4],
    'adx': __VALIDATORS__[5],
    'obv': __VALIDATORS__[6],
    'pairs': __VALIDATORS__[7],
    'all': __VALIDATORS__
}
