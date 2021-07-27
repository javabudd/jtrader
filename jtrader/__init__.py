import math
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def chunks(chunk_data, n: int):
    for i in range(0, len(chunk_data), n):
        yield chunk_data[i:i + n]


def chunk_threaded(dictionary: dict, is_sandbox=False, chunk_size: int = 25):
    num_lines = len(dictionary)
    chunk_size = math.floor(num_lines / chunk_size)
    if is_sandbox:
        chunk_size = math.floor(num_lines / 2)

    return list(chunks(dictionary, chunk_size))
