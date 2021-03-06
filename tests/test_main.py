from jtrader.main import JTraderTest


def test_jtrader():
    # test jtrader without any subcommands or arguments
    with JTraderTest() as app:
        app.run()
        assert app.exit_code == 0


def test_jtrader_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with JTraderTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_start_backtest():
    argv = ['start-backtest', '-t', 'FOO', '-b', 'rsi', '-s', 'volume']
    with JTraderTest(argv=argv) as app:
        app.run()
        data, output = app.last_rendered
        assert data['results'] is None
