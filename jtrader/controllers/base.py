import pyEX as IEXClient
from cement import Controller, ex
from cement.utils.version import get_version_banner

from jtrader.core.backtester import Backtester
from jtrader.core.news import News
from jtrader.core.scanner.hqm import HighQualityMomentum
from jtrader.core.scanner.lqm import LowQualityMomentum
from jtrader.core.scanner.momentum import Momentum
from jtrader.core.scanner.premarketmomentum import PreMarketMomentum
from jtrader.core.scanner.scanner import Scanner
from jtrader.core.scanner.value import Value
from jtrader.core.secrets import IEX_CLOUD_API_TOKEN, IEX_CLOUD_SANDBOX_API_TOKEN
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
    'volume'
]


class Base(Controller):
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
    def get_iex_client(is_sandbox: bool, version: str = 'stable'):
        token = IEX_CLOUD_API_TOKEN
        if is_sandbox:
            version = 'sandbox'
            token = IEX_CLOUD_SANDBOX_API_TOKEN

        return IEXClient.Client(token, version)

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()

    @ex(
        help='Start the worker',
        arguments=[],
    )
    def start_worker(self):
        """Start Worker Command"""
        worker = Worker(self.get_iex_client(False), self.app.log)

        worker.run()

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

        data = {
            'news_stream': News(is_sandbox, self.app.log),
        }

        self.app.render(data, 'start_news_stream.jinja2')

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

        data = {
            'stats': LowQualityMomentum(is_sandbox, self.app.log),
        }

        self.app.render(data, 'get_lqm_stats.jinja2')

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

        data = {
            'stats': HighQualityMomentum(is_sandbox, self.app.log),
        }

        self.app.render(data, 'get_hqm_stats.jinja2')

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

        data = {
            'stats': Value(is_sandbox, self.app.log),
        }

        self.app.render(data, 'get_value_stats.jinja2')

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

        PreMarketMomentum(is_sandbox, self.app.log).run()

        self.app.render({}, 'start_pmm_scanner.jinja2')

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

        Momentum(is_sandbox, self.app.log).run()

        self.app.render({}, 'start_mm_scanner.jinja2')

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
            self.app.log,
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
            self.app.log,
            self.app.pargs.indicators,
            None,
            None,
            False,
            self.app.pargs.no_notifications
        ).run()

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
    def run_backtest(self):
        """Start Run Backtest Command"""
        backtester = Backtester(
            self.app.log,
            self.app.pargs.ticker,
            self.app.pargs.start_date,
            self.app.pargs.end_date,
        )

        backtester.run()
