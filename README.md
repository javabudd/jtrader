# Trade them thangs

![JTrader](https://github.com/javabudd/jtrader/actions/workflows/ubuntu.yml/badge.svg?branch=main)

## Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run jtrader cli application

$ jtrader --help


### run pytest / coverage

$ make test
```

## Commands

### get-mm-stats

Get Current Market Momentum Statistics

This command will output market momentum statistics to a CSV and/or slack

More information: `jtrader get-mm-stats --help`

### get-pmm-stats

Get Pre-Market Momentum Statistics

This command will output pre-market momentum statistics to a CSV and/or slack

More information: `jtrader get-pmm-stats --help`

### get-hqm-stats

Get High Quality Momentum Statistics

This command will output high quality market momentum statistics to a CSV and/or slack

More information: `jtrader get-hqm-stats --help`

### get-value-stats

Get Deep Value Statistics

This command will output deep value stocks to a CSV and/or slack

More information: `jtrader get-value-stats --help`

### start-worker

Start Worker

Starts the background worker to populate the DB with stock prices

More information: `jtrader start-worker --help`

### start-scanner

Start Stock Scanner

Starts the stock scanner, returning bearish or bullish results depending on configuration

More information: `jtrader start-scanner --help`

### start-intraday-scanner

Start Intraday Stock Scanner

Starts the intraday stock scanner, returning bearish or bullish results depending on configuration

More information: `jtrader start-intraday-scanner --help`

### start-news-stream

Start News Stream

Starts the background news stream process, outputting to the specified notification platform

More information: `jtrader start-news-stream --help`

### start-backtest

Start a Backtest against a specific algorithm/s

Starts the zipline backtest using buy/sell strategies provided

More information: `jtrader start-backtest --help`

### start-kucoin-trader

Start the KuCoin trader

Starts the kucoin trader and print out buy/sell signals on all indicators

More information: `jtrader start-kucoin-trader --help`

## Deployments

### Docker

Included is a basic `Dockerfile` for building and distributing `JTrader`, and can be built with the included `make`
helper:

```
$ make docker

$ docker run -it jtrader --help
```
