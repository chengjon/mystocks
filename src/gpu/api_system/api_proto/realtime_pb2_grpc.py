
class RealTimeServiceServicer:
    def StreamMarketData(self, request_iterator, context):
        raise NotImplementedError
    def ComputeFeatures(self, request, context):
        raise NotImplementedError

def add_RealTimeServiceServicer_to_server(servicer, server):
    pass
