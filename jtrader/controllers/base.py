from cement import Controller, ex
from cement.utils.version import get_version_banner

from jtrader.core.momentum import Momentum
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
            'news_stream': News(),
        }

        # if self.app.pargs.foo is not None:
        #     data['foo'] = self.app.pargs.foo

        self.app.render(data, 'start_news_stream.jinja2')

    @ex(
        help='Get momentum stats',

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
    def get_momentum_stats(self):
        """Momentum Stats Command"""

        data = {
            'stats': Momentum(self.app.config.get('jtrader', 'is_sandbox')),
        }

        self.app.render(data, 'get_momentum_stats.jinja2')

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
