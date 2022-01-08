import itertools
from pathlib import Path
from typing import Union, Optional

import numpy as np
import pandas as pd
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation, performance_metrics

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
        param_grid = {
            'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
            'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
        }

        data = self.data.data

        all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
        rmses = []

        for params in all_params:
            model = Prophet(**params)

            if regressors is not None:
                for regressor_name in regressors.keys():
                    model.add_regressor(regressor_name)
                    data[regressor_name] = regressors[regressor_name]

            data.replace([np.inf, -np.inf, np.nan], 0, inplace=True)

            model.fit(data)
            df_cv = cross_validation(model, horizon='30 days', parallel="processes")
            df_p = performance_metrics(df_cv, rolling_window=1)
            rmses.append(df_p['rmse'].values[0])

        tuning_results = pd.DataFrame(all_params)
        tuning_results['rmse'] = rmses
        best_params = all_params[np.argmin(rmses)]

        model = Prophet(**best_params)

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
