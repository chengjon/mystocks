class TrainModelRequest:
    def __init__(self, **kwargs):
        self.model_type = kwargs.get("model_type", "")
        self.training_data = kwargs.get("training_data", "")
        self.feature_columns = kwargs.get("feature_columns", [])
        self.target_column = kwargs.get("target_column", "")
        self.model_params = kwargs.get("model_params", "")


class TrainModelResponse:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class PredictRequest:
    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", "")
        self.input_data = kwargs.get("input_data", "")


class PredictResponse:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ModelMetrics:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TrainingStatus:
    FAILED = "failed"
    QUEUED = "queued"
    TRAINING = "training"
    COMPLETED = "completed"

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
