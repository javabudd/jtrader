import pandas as pd
from cement import Controller, ex
from cement.utils.version import get_version_banner

from jtrader.core.hqm import HighQualityMomentum
from jtrader.core.lqm import LowQualityMomentum
from jtrader.core.momentum import Momentum
from jtrader.core.news import News
from jtrader.core.premarketmomentum import PreMarketMomentum
from jtrader.core.scanner.scanner import Scanner
from jtrader.core.value import Value
from ..core.version import get_version

VERSION_BANNER = """
Trade them thangs %s
%s
""" % (get_version(), get_version_banner())

indicators = [
    'robust',
    'simple',
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

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()

    @ex(
        help='Process a backtest file into CSV'
    )
    def process_backtest(self):
        def process_performance(file_name):
            perf = pd.read_pickle('{}.pickle'.format(file_name))
            perf.to_csv('{}.csv'.format(file_name))
            perf.index = perf.index.normalize()

            return perf

        process_performance(file_name='out')

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
        ],
    )
    def start_intraday_scanner(self):
        """Start Scanner Command"""
        is_sandbox = self.app.pargs.is_sandbox

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        Scanner(is_sandbox, self.app.log, self.app.pargs.indicators, self.app.pargs.stock_list).run()

        self.app.render({}, 'start_scanner.jinja2')

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

        self.app.render({}, 'start_scanner.jinja2')
