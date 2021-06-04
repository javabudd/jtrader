from .apo import APOValidator
from .coc import COCValidator
from .robust import RobustValidator
from .rsi import RSIValidator
from .ultosc import ULTOSCValidator
from .macd import MACDValidator

__VALIDATORS__ = [
    APOValidator,
    ULTOSCValidator,
    RobustValidator,
    RSIValidator,
    COCValidator,
    MACDValidator
]

__VALIDATION_MAP__ = {
    'apo': __VALIDATORS__[0],
    'ultosc': __VALIDATORS__[1],
    'robust': __VALIDATORS__[2],
    'rsi': __VALIDATORS__[3],
    'coc': __VALIDATORS__[4],
    'macd': __VALIDATORS__[5],
    'all': __VALIDATORS__
}
