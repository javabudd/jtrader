def timeframe_to_days(timeframe, as_stock_frame: bool = False) -> int:
    if timeframe.find('d') != -1:
        return int(timeframe.strip('d')) if as_stock_frame else int(timeframe.strip('d')) + 2

    if timeframe.find('m') != -1:
        return int(timeframe.strip('m')) * 30

    if timeframe.find('y') != -1:
        year = timeframe.strip('y')

        return int(year) * 252 if as_stock_frame else int(year) * 365

    raise ValueError
