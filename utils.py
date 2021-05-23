def chunks(lst, n):
    for item in range(0, len(lst), n):
        yield lst[item:item + n]