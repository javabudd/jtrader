from .adx import ADX
from .apo import APO
from .chaikin import Chaikin
from .linear_regression import LinearRegression
from .macd import MACD
from .obv import OBV
from .rsi import RSI
from .ultosc import ULTOSC

__INDICATORS__ = [
    APO,
    ULTOSC,
    RSI,
    MACD,
    Chaikin,
    ADX,
    OBV,
    LinearRegression
]

__INDICATOR_MAP__ = {
    'apo': __INDICATORS__[0],
    'ultosc': __INDICATORS__[1],
    'rsi': __INDICATORS__[2],
    'macd': __INDICATORS__[3],
    'chaikin': __INDICATORS__[4],
    'adx': __INDICATORS__[5],
    'obv': __INDICATORS__[6],
    'lr': __INDICATORS__[7],
    'all': __INDICATORS__
}
