from .adx import ADX
from .apo import APO
from .adosc import ADOSC
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
    ADOSC,
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
    'adosc': ADOSC,
    'adx': ADX,
    'obv': OBV,
    'lr': LinearRegression,
    'vwap': VWAP,
    'all': __INDICATORS__
}
