
from collections import deque
from threading import Lock
import time

class RateLimiter:
    
    def __init__(self, max_requests: int, window_seconds:int):
        
        if max_requests <=0 or window_seconds <= 0:
            raise ValueError("Rate limit values must be positive")
        
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        self.request_timestamps = deque()
        self.lock = Lock()
        
    
    def acquire(self) -> None:
        while True:
            
            with self.lock:
                current_time = time.monotonic()

                while (
                    self.request_timestamps
                    and current_time - self.request_timestamps[0]
                    >= self.window_seconds
                ):
                    self.request_timestamps.popleft()
                # appened to the queue
                if len(self.request_timestamps) < self.max_requests:
                    self.request_timestamps.append(current_time)
                    return

                # calculate the waiting time
                wait_time = (
                    self.window_seconds
                    - (current_time - self.request_timestamps[0])
                )

            time.sleep(wait_time)