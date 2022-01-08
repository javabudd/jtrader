from pathlib import Path
from typing import Union, Optional

import numpy as np
import pandas as pd
from fbprophet import Prophet

from jtrader.core.machine_learning.base_model import BaseModel

MODEL_FOLDER = 'models'


class LocalLinearLearner(BaseModel):
    container_name: str = "linear-learner"
    name: str = "linear_learner"

    default_tuning_job_config = {
        "max_jobs": 20,
        "max_parallel_jobs": 3,
        "objective_metric_name": "validation:objective_loss",
        "objective_type": "Minimize",
    }

    def __init__(self, data, stock: str, timeframe: str = '5y'):
        super().__init__(data)

        self.stock = stock
        self.timeframe = timeframe
        self._model = None

    @staticmethod
    def save_model(model, name: str) -> None:
        try:
            Path(MODEL_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(model, f"{MODEL_FOLDER}/{name}.pkl")

    def train(self, regressors: Optional[dict] = None) -> Prophet:
        model = Prophet(daily_seasonality=True)
        data = self.data.data

        if regressors is not None:
            for regressor_name in regressors.keys():
                model.add_regressor(regressor_name)
                data[regressor_name] = regressors[regressor_name]

        data.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

        model.fit(data)

        return model

    def tune(self) -> None:
        pass

    def load_model(self, model_name: str = "") -> Union[bool, pd.DataFrame]:
        path = Path(f"{MODEL_FOLDER}/{model_name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{MODEL_FOLDER}/{model_name}.pkl")
        else:
            model = False

        self._model = model

        return model

    def execute_prediction(self, data: pd.DataFrame, name: str = "test") -> pd.DataFrame:
        return pd.DataFrame(self._model.predict(data))
