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
        help='Start a news stream',

        arguments=[
            (
                    ['-f', '--foo'],
                    {
                        'help': 'notorious foo option',
                        'action': 'store',
                        'dest': 'foo'
                    }
            ),
        ],
    )
    def start_news_stream(self):
        """News Stream Command"""

        data = {
            'news_stream': News(self.app.config.get('jtrader', 'is_sandbox'), self.app.log),
        }

        # if self.app.pargs.foo is not None:
        #     data['foo'] = self.app.pargs.foo

        self.app.render(data, 'start_news_stream.jinja2')

    @ex(
        help='Get low quality momentum stats',

        arguments=[
            (
                    ['-f', '--foo'],
                    {
                        'help': 'notorious foo option',
                        'action': 'store',
                        'dest': 'foo'
                    }
            ),
        ],
    )
    def get_lqm_stats(self):
        """LQM Stats Command"""

        data = {
            'stats': LowQualityMomentum(self.app.config.get('jtrader', 'is_sandbox'), self.app.log),
        }

        self.app.render(data, 'get_lqm_stats.jinja2')

    @ex(
        help='Get high quality momentum stats',

        arguments=[
            (
                    ['-f', '--foo'],
                    {
                        'help': 'notorious foo option',
                        'action': 'store',
                        'dest': 'foo'
                    }
            ),
        ],
    )
    def get_hqm_stats(self):
        """HQM Stats Command"""

        data = {
            'stats': HighQualityMomentum(self.app.config.get('jtrader', 'is_sandbox'), self.app.log),
        }

        self.app.render(data, 'get_hqm_stats.jinja2')

    @ex(
        help='Get deep value stats',

        arguments=[
            (
                    ['-f', '--foo'],
                    {
                        'help': 'notorious foo option',
                        'action': 'store',
                        'dest': 'foo'
                    }
            ),
        ],
    )
    def get_value_stats(self):
        """Deep Value Stats Command"""

        data = {
            'stats': Value(self.app.config.get('jtrader', 'is_sandbox'), self.app.log),
        }

        self.app.render(data, 'get_value_stats.jinja2')

    @ex(
        help='Get pre market momentum stats',

        arguments=[
            (
                    ['-f', '--foo'],
                    {
                        'help': 'notorious foo option',
                        'action': 'store',
                        'dest': 'foo'
                    }
            ),
        ],
    )
    def get_pmm_stats(self):
        """Start Pre Market Momentum Scanner Command"""

        PreMarketMomentum(self.app.config.get('jtrader', 'is_sandbox'), self.app.log).run()

        self.app.render({}, 'start_pmm_scanner.jinja2')

    @ex(
        help='Get market momentum stats',

        arguments=[
            (
                    ['-f', '--foo'],
                    {
                        'help': 'notorious foo option',
                        'action': 'store',
                        'dest': 'foo'
                    }
            ),
        ],
    )
    def get_mm_stats(self):
        """Start Market Momentum Scanner Command"""
        is_sandbox = self.app.config.get('jtrader', 'is_sandbox')

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        Momentum(is_sandbox, self.app.log).run()

        self.app.render({}, 'start_mm_scanner.jinja2')

    @ex(
        help='Start stock scanner',

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
                        'choices': [
                            'robust',
                            'apo',
                            'ultosc',
                            'rsi',
                            'macd',
                            'coc'
                        ],
                        'nargs': '+'
                    }
            ),
        ],
    )
    def start_scanner(self):
        """Start Scanner Command"""
        is_sandbox = self.app.config.get('jtrader', 'is_sandbox')

        if is_sandbox:
            self.app.log.info('Starting in sandbox mode...')

        Scanner(is_sandbox, self.app.log, self.app.pargs.stock_list, self.app.pargs.indicators).run()

        self.app.render({}, 'start_scanner.jinja2')
