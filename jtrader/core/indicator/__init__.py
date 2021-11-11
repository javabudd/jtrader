from .adx import ADX
from .apo import APO
from .chaikin import Chaikin
from .linear_regression import LinearRegression
from .macd import MACD
from .obv import OBV
from .rsi import RSI
from .ultosc import ULTOSC
from .vwap import VWAP

__INDICATORS__ = [
    APO,
    ULTOSC,
    RSI,
    MACD,
    Chaikin,
    ADX,
    OBV,
    LinearRegression,
    VWAP
]

__INDICATOR_MAP__ = {
    'apo': APO,
    'ultosc': ULTOSC,
    'rsi': RSI,
    'macd': MACD,
    'chaikin': Chaikin,
    'adx': ADX,
    'obv': OBV,
    'lr': LinearRegression,
    'vwap': VWAP,
    'all': __INDICATORS__
}
