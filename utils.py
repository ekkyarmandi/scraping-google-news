import time

def elapsed_time(function):
    def wrapper(*args, **kwargs):
        start = time.time()
        results = function(*args, **kwargs)
        end = time.time()
        delta = end - start
        print(f"Elapsed Time {delta:.2f}")
        return results
    return wrapper