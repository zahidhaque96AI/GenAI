
import time
from src.ratelimiter import RateLimiter

limiter = RateLimiter(
    max_requests=2, 
    window_seconds=5,
)

for i in range(5):

    start = time.monotonic()

    limiter.acquire()

    elapsed = time.monotonic() - start

    print(
        f"Request {i + 1} permitted. "
        f"Waited: {elapsed:.2f} seconds"
    )
    