import logging

from cement import Controller, ex
from cement.utils.version import get_version_banner

from jtrader.core.backtester import Backtester
from jtrader.core.ml import ALGORITHMS
from jtrader.core.ml import ML
from jtrader.core.news import News
from jtrader.core.provider import IEX
from jtrader.core.provider import KuCoin as KuCoinProvider
from jtrader.core.provider import LoopRing as LoopRingProvider
from jtrader.core.scanner.hqm import HighQualityMomentum
from jtrader.core.scanner.lqm import LowQualityMomentum
from jtrader.core.scanner.momentum import Momentum
from jtrader.core.scanner.premarketmomentum import PreMarketMomentum
from jtrader.core.scanner.scanner import Scanner
from jtrader.core.scanner.value import Value
from jtrader.core.trader import KuCoin
from jtrader.core.trader import LoopRing
from jtrader.core.trader import Pairs
from jtrader.core.worker import Worker
from ..core.version import get_version

VERSION_BANNER = """
Trade them thangs %s
%s
""" % (get_version(), get_version_banner())

indicators = [
    'apo',
    'ultosc',
    'rsi',
    'macd',
    'coc',
    'adx',
    'obv',
    'chaikin',
    'pairs',
    'lr',
    'volume'
]


class Base(Controller):
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    class Meta:
        label = 'base'
        description = 'Trade them thangs'
        epilog = 'Usage: jtrader {command} {args}'
        arguments = [
            (
                ['-v', '--version'],
                {
                    'action': 'version',
                    'version': VERSION_BANNER
                }
            ),
        ]

    @staticmethod
    def get_iex_provider(is_sandbox: bool, version: str = 'stable') -> IEX:
        return IEX(is_sandbox, version)

    @staticmethod
    def get_kucoin_provider(is_sandbox: bool) -> KuCoinProvider:
        return KuCoinProvider(is_sandbox)

    @staticmethod
    def get_loopring_provider(is_sandbox: bool) -> LoopRingProvider:
        return LoopRingProvider(is_sandbox)

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()

    @ex(
        help='Start the worker',
        arguments=[],
    )
    def start_worker(self):
        """Start Worker Command"""
        results = Worker(self.get_iex_provider(False), self.app.log).run()

        self.app.render({'results': results}, 'start_worker.jinja2')

    @ex(
        help='Start a news stream',
        arguments=[
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def start_news_stream(self):
        """News Stream Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        results = News(is_sandbox, self.app.log).run()

        self.app.render({'results': results}, 'start_news_stream.jinja2')

    @ex(
        help='Get low quality momentum stats',
        arguments=[
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def get_lqm_stats(self):
        """LQM Stats Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        results = LowQualityMomentum(is_sandbox, self.app.log).run()

        self.app.render({'results': results}, 'get_lqm_stats.jinja2')

    @ex(
        help='Get high quality momentum stats',
        arguments=[
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def get_hqm_stats(self):
        """HQM Stats Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        results = HighQualityMomentum(is_sandbox, self.app.log).run()

        self.app.render({'results': results}, 'get_hqm_stats.jinja2')

    @ex(
        help='Get deep value stats',
        arguments=[
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def get_value_stats(self):
        """Deep Value Stats Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        results = Value(is_sandbox, self.app.log).run()

        self.app.render({'results': results}, 'get_value_stats.jinja2')

    @ex(
        help='Get pre market momentum stats',
        arguments=[
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def get_pmm_stats(self):
        """Start Pre Market Momentum Scanner Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        results = PreMarketMomentum(is_sandbox, self.app.log).run()

        self.app.render({'results': results}, 'start_pmm_scanner.jinja2')

    @ex(
        help='Get market momentum stats',
        arguments=[
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def get_mm_stats(self):
        """Start Market Momentum Scanner Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        results = Momentum(is_sandbox, self.app.log).run()

        self.app.render({"results": results}, 'start_mm_scanner.jinja2')

    @ex(
        help='Start intraday stock scanner',
        arguments=[
            (
                    ['-s', '--stock-list'],
                    {
                        'help': 'change the default stock list',
                        'action': 'store',
                        'dest': 'stock_list',
                        'choices': [
                            'sp500',
                            'all'
                        ]
                    }
            ),
            (
                    ['-t', '--technical-indicators'],
                    {
                        'help': 'which technicals indicators to scan against',
                        'action': 'append',
                        'dest': 'indicators',
                        'choices': indicators,
                        'nargs': '+'
                    }
            ),
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
            (
                    ['--no-notifications'],
                    {
                        'help': 'disable notifications',
                        'action': 'store_true',
                        'dest': 'no_notifications'
                    }
            ),
        ],
    )
    def start_intraday_scanner(self):
        """Start Scanner Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        Scanner(
            is_sandbox,
            self.app.pargs.indicators,
            self.app.pargs.stock_list,
            no_notifications=self.app.pargs.no_notifications
        ).run()

    @ex(
        help='Start stock scanner',
        arguments=[
            (
                    ['-t', '--technical-indicators'],
                    {
                        'help': 'which technicals indicators to scan against',
                        'action': 'append',
                        'dest': 'indicators',
                        'choices': indicators,
                        'nargs': '+'
                    }
            ),
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
            (
                    ['--no-notifications'],
                    {
                        'help': 'disable notifications',
                        'action': 'store_true',
                        'dest': 'no_notifications'
                    }
            ),
        ],
    )
    def start_scanner(self):
        """Start Scanner Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        Scanner(
            is_sandbox,
            self.app.pargs.indicators,
            as_intraday=False,
            no_notifications=self.app.pargs.no_notifications
        ).run()

    @ex(
        help='Start ML Trainer',
        arguments=[
            (
                    ['-t', '--ticker'],
                    {
                        'help': 'Ticker to process',
                        'action': 'store',
                        'dest': 'ticker',
                        'required': True
                    }
            ),
            (
                    ['-a', '--algorithm'],
                    {
                        'help': 'which algorithm to use',
                        'action': 'store',
                        'dest': 'algorithm',
                        'choices': ALGORITHMS,
                        'required': True
                    }
            ),
            (
                    ['--with-aws'],
                    {
                        'help': 'use AWS to train',
                        'action': 'store_true',
                        'dest': 'with_aws'
                    }
            ),
            (
                    ['--with-numerai'],
                    {
                        'help': 'use Numerai to train/populate',
                        'action': 'store_true',
                        'dest': 'with_numerai'
                    }
            ),
            (
                    ['--dask-cluster-address'],
                    {
                        'help': 'Dask cluster address to perform cross validation on',
                        'action': 'store',
                        'dest': 'dask_cluster_address'
                    }
            ),
        ],
    )
    def start_ml_trainer(self):
        """Start ML Trainer Command"""
        ML(self.get_iex_provider(False)).run_trainer(
            self.app.pargs.ticker,
            self.app.pargs.algorithm,
            self.app.pargs.with_aws,
            self.app.pargs.with_numerai,
            self.app.pargs.dask_cluster_address,
        )

    @ex(
        help='Start ML Predictor',
        arguments=[
            (
                    ['-p', '--predictions'],
                    {
                        'help': 'the prediction list',
                        'action': 'append',
                        'dest': 'predictions',
                        'required': True,
                        'nargs': '+',
                        'type': float
                    }
            ),
            (
                    ['-m', '--model'],
                    {
                        'help': 'the model to use',
                        'action': 'store',
                        'dest': 'model',
                        'required': True,
                        'nargs': '+',
                        'type': str
                    }
            ),
        ],
    )
    def start_ml_predictor(self):
        """Start ML Predictor Command"""

        ML(self.get_iex_provider(False)).run_predictor(self.app.pargs.model[0], self.app.pargs.predictions)

    @ex(
        help='Start Dask Worker',
        arguments=[
            (
                    ['-a', '--address'],
                    {
                        'help': 'Cluster address to connect to',
                        'action': 'store',
                        'dest': 'address',
                        'required': True
                    }
            ),
            (
                    ['-c', '--contact-address'],
                    {
                        'help': 'Contact address to listen to',
                        'action': 'store',
                        'dest': 'contact_address',
                    }
            ),
            (
                    ['-l', '--listen-address'],
                    {
                        'help': 'Worker address to listen on',
                        'action': 'store',
                        'dest': 'listen_address',
                        'required': True
                    }
            ),
            (
                    ['-lp', '--listen-address-port'],
                    {
                        'help': 'Worker port to listen on',
                        'action': 'store',
                        'dest': 'listen_address_port',
                        'required': True,
                        'type': int
                    }
            ),
        ],
    )
    def start_dask_worker(self):
        """Start Dask Worker Command"""
        ML(self.get_iex_provider(False)).start_dask_worker(
            self.app.pargs.address,
            self.app.pargs.listen_address,
            self.app.pargs.listen_address_port,
            self.app.pargs.contact_address,
        )

    @ex(
        help='Start Dask Scheduler',
        arguments=[],
    )
    def start_dask_scheduler(self):
        """Start Dask Worker Command"""
        ML(self.get_iex_provider(False)).start_dask_scheduler()

    @ex(
        help='Run a backtest',
        arguments=[
            (
                    ['-t', '--ticker'],
                    {
                        'help': 'Ticker to process',
                        'action': 'store',
                        'dest': 'ticker',
                        'required': True
                    }
            ),
            (
                    ['-b', '--buy-indicators'],
                    {
                        'help': 'which technicals indicators to buy against',
                        'action': 'append',
                        'dest': 'buy_indicators',
                        'choices': indicators,
                        'nargs': '+',
                        'required': True
                    }
            ),
            (
                    ['-s', '--sell-indicators'],
                    {
                        'help': 'which technicals indicators to sell against',
                        'action': 'append',
                        'dest': 'sell_indicators',
                        'choices': indicators,
                        'nargs': '+',
                        'required': True
                    }
            ),
            (
                    ['--start'],
                    {
                        'help': 'Backtest start date',
                        'action': 'store',
                        'dest': 'start_date'
                    }
            ),
            (
                    ['--end'],
                    {
                        'help': 'Backtest end date',
                        'action': 'store',
                        'dest': 'end_date'
                    }
            ),
        ],
    )
    def start_backtest(self):
        """Start Backtest Command"""
        backtester = Backtester(
            self.app.log,
            self.app.pargs.ticker,
            self.app.pargs.start_date,
            self.app.pargs.end_date,
            self.app.pargs.buy_indicators,
            self.app.pargs.sell_indicators,
        )

        results = backtester.run()

        self.app.render({'results': results}, 'start_backtester.jinja2')

    @ex(
        help='Run the trader',
        arguments=[
            (
                    ['-x', '--exchange'],
                    {
                        'help': 'which exchange to run against',
                        'action': 'store',
                        'dest': 'exchange',
                        'required': True,
                        'choices': [
                            'kucoin',
                            'loopring',
                            'pairs'
                        ],
                    }
            ),
            (
                    ['-t', '--ticker'],
                    {
                        'help': 'which ticker to trader',
                        'action': 'store',
                        'dest': 'ticker',
                        'required': True
                    }
            ),
            (
                    ['--sandbox'],
                    {
                        'help': 'start in sandbox mode',
                        'action': 'store_true',
                        'dest': 'is_sandbox'
                    }
            ),
        ],
    )
    def start_trader(self):
        """Start trader Command"""
        exchange = self.app.pargs.exchange

        trader = None
        if exchange == 'kucoin':
            trader = KuCoin(self.get_kucoin_provider(self.app.pargs.is_sandbox), self.app.pargs.ticker)
        elif exchange == 'loopring':
            trader = LoopRing(self.get_loopring_provider(self.app.pargs.is_sandbox), self.app.pargs.ticker)
        elif exchange == 'pairs':
            trader = Pairs(self.get_iex_provider(self.app.pargs.is_sandbox), self.app.pargs.ticker)

        if trader is None:
            raise RuntimeError

        trader.start_trader()
