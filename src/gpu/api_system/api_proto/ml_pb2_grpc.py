class MLServiceServicer:
    def TrainModel(self, request, context):
        raise NotImplementedError

    def Predict(self, request, context):
        raise NotImplementedError

    def GetTrainingStatus(self, request, context):
        raise NotImplementedError

    def GetModelMetrics(self, request, context):
        raise NotImplementedError


def add_MLServiceServicer_to_server(servicer, server):
    pass
