
class BacktestRequest:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, 'stock_codes'): self.stock_codes = []
        if not hasattr(self, 'start_time'): self.start_time = ""
        if not hasattr(self, 'end_time'): self.end_time = ""
        if not hasattr(self, 'strategy_config'): self.strategy_config = ""
        if not hasattr(self, 'initial_capital'): self.initial_capital = 0.0
        if not hasattr(self, 'commission_rate'): self.commission_rate = 0.0

class BacktestResponse:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class BacktestStatus:
    FAILED = "failed"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class BacktestResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class PerformanceMetrics:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
