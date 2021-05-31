from cement import Controller, ex
from cement.utils.version import get_version_banner

from jtrader.core.hqm import HighQualityMomentum
from jtrader.core.lqm import LowQualityMomentum
from jtrader.core.scanner.premarketmomentum import PreMarketMomentum
from jtrader.core.news import News
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
            'news_stream': News(self.app.config.get('jtrader', 'is_sandbox')),
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
            'stats': LowQualityMomentum(self.app.config.get('jtrader', 'is_sandbox')),
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
            'stats': HighQualityMomentum(self.app.config.get('jtrader', 'is_sandbox')),
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
            'stats': Value(self.app.config.get('jtrader', 'is_sandbox')),
        }

        self.app.render(data, 'get_value_stats.jinja2')

    @ex(
        help='Start Pre Market Momentum Scanner',

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
    def start_pmm_scanner(self):
        """Start Pre Market Momentum Scanner Command"""

        data = {
            'scanner': PreMarketMomentum(self.app.config.get('jtrader', 'is_sandbox')),
        }

        self.app.render(data, 'start_pmm_scanner.jinja2')
