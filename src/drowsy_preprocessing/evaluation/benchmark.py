import time


def benchmark(function, items):
    start = time.perf_counter()
    count = 0
    for item in items:
        function(item)
        count += 1
    elapsed = time.perf_counter() - start
    return {
        "items": count,
        "elapsed_s": elapsed,
        "items_per_s": count / elapsed if elapsed else None,
    }
