## Project Overview

JTrader is a algorithmic trading and market analysis CLI application built using the [Cement Framework](https://builtoncement.com/). It supports market scanning, backtesting, and automated trading across various providers.

## Dependencies & Environment

This project uses Conda to manage environments. 

- **Environment Name**: `jtrader`
- **Python Version**: 3.14 (per `README.md`)
- **Commands**: Always use the conda environment when calling python or jtrader commands. 
  - Example: `conda activate jtrader && python ...` or `conda activate jtrader && jtrader --help`

### Alternative Environment Helpers
The project includes a `Makefile` with common tasks:
- `make virtualenv`: Creates a traditional virtualenv (if not using Conda).
- `make test`: Runs pytest with coverage.
- `make docker`: Builds the JTrader Docker image.

## Project Structure

All source code is located in the `jtrader/` directory.

- `jtrader/main.py`: Application entry point and Cement App definition.
- `jtrader/controllers/`: CLI command handlers. `base.py` contains most command definitions.
- `jtrader/core/`: Core business logic:
    - `backtester.py`: Logic for running backtests.
    - `indicator/`: Technical indicators (RSI, MACD, ADX, etc.).
    - `machine_learning/`: ML models (local and AWS SageMaker integrations).
    - `provider/`: Data provider integrations (IEX, KuCoin, Loopring).
    - `scanner/`: Market scanning logic (Momentum, Value, HQM, etc.).
    - `trader/`: Execution logic for different exchanges.
- `jtrader/templates/`: Jinja2 templates for CLI output and reports.
- `config/`: Configuration examples. The app expects `jtrader.yml`.

## Common Commands

- `jtrader get-mm-stats`: Get Market Momentum stats.
- `jtrader start-scanner`: Start the stock scanner.
- `jtrader start-backtest`: Run backtests against algorithms.
- `jtrader start-trader`: Start the automated trader.

## Configuration

JTrader uses YAML for configuration. Copy `config/jtrader.yml.example` to `jtrader.yml` (usually in `~/.jtrader/` or the project root) to get started. Key settings include `is_sandbox` for API testing.
