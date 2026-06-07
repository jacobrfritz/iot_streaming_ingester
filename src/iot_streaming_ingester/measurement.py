from typing import Protocol

"""
- receives real time data from stream and accumulates metrics
"""

class Measurement(Protocol): 
    def measure(self, window): ...






"""
def get_metrics(self, messages: RedisStreamResponse) -> tuple[int, float, float]:
        # Chan's Parallel Variance
        # returns count, mean, and running sum of squares for variance
        # needs to calculate for each producer
        mean = int()
        ss = float()
        for count, message in enumerate(messages):
            delta = float()
            print(message)
        return 100, mean, ss
"""
