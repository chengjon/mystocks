
class StreamDataRequest:
    def __init__(self, **kwargs):
        self.stock_code = kwargs.get('stock_code', '')
        self.price = kwargs.get('price', 0.0)
        self.volume = kwargs.get('volume', 0)
        self.timestamp = kwargs.get('timestamp', '')

class StreamDataResponse:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class FeatureRequest:
    def __init__(self, **kwargs):
        self.stock_code = kwargs.get('stock_code', '')
        self.feature_types = kwargs.get('feature_types', [])

class FeatureResponse:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
