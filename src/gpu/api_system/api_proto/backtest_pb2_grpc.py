class BacktestServiceServicer:
    def RunBacktest(self, request, context):
        raise NotImplementedError

    def GetBacktestStatus(self, request, context):
        raise NotImplementedError

    def GetBacktestResult(self, request, context):
        raise NotImplementedError


def add_BacktestServiceServicer_to_server(servicer, server):
    pass
