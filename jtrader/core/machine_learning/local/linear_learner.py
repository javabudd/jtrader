import hashlib
import itertools
import json
from pathlib import Path
from typing import Union, Optional

import numpy as np
import pandas as pd
from pandas import DataFrame
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from jtrader.core.machine_learning.base_model import BaseModel
from jtrader.core.odm import ODM
from .data_loader import DataLoader

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

    def __init__(self, data, stock: str, timeframe: str = '5y', model_name: str = None):
        super().__init__(data, model_name)

        self.stock = stock
        self.timeframe = timeframe
        self._model = None
        self.db = ODM()

    @staticmethod
    def save_model(model, name: str) -> None:
        try:
            Path(MODEL_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(model, f"{MODEL_FOLDER}/{name}.pkl")

    def get_prophet_model(self, prophet_params: dict, extra_features: dict = None):
        model = Prophet(**prophet_params)

        if extra_features is not None:
            for feature in extra_features.keys():
                model.add_regressor(feature)
                if feature not in self.data.data:
                    df = extra_features[feature]
                    df.reset_index(level=0, inplace=True)
                    df.rename(columns={"date": "ds"}, inplace=True)
                    df.fillna(extra_features[feature].mean(), inplace=True)
                    self.data.data['ds'] = self.data.data['ds'].astype('datetime64[ns]')
                    df['ds'] = df['ds'].astype('datetime64[ns]')
                    data = pd.merge(self.data.data, df, on='ds')
                    self.data._data = data

        return model

    def load_model(self, model_name: str = "") -> Union[bool, pd.DataFrame]:
        path = Path(f"{MODEL_FOLDER}/{model_name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{MODEL_FOLDER}/{model_name}.pkl")
        else:
            model = False

        self._model = model

        return model

    def train(
            self,
            hyperparameters: Optional[dict] = None,
            extra_features: Optional[dict] = None,
            dask_cluster_address: Optional[str] = None
    ) -> Prophet:
        if hyperparameters is None or len(hyperparameters) == 0:
            hyperparameters = self.db.get_prophet_params(self.stock, self.model_name)

        # if there are no hyperparameters provided, run auto-tuning
        if hyperparameters is None:
            seasonality_grid = {
                'fourier': [0.005, .01, 0.05, 0.5, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                'prior_scale': [0.005, .01, 0.05, 0.5, 1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            }

            param_grid = {
                'changepoint_prior_scale': [0.001, 0.01, 0.1, 0.5],
                'seasonality_prior_scale': [0.01, 0.1, 1.0, 10.0],
                'seasonality_mode': ['additive', 'multiplicative']
            }

            fitted_models = {}
            all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
            rmses = []

            for params in all_params:
                param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode('utf-8')).hexdigest()
                model = self.get_prophet_model(params, extra_features)

                model.fit(self.data.data)

                fitted_models[param_hash] = model

                mode = 'processes'
                if dask_cluster_address:
                    from distributed import Client
                    Client(address=dask_cluster_address)
                    mode = 'dask'

                df_cv = cross_validation(model, horizon='30 days', parallel=mode)
                df_p = performance_metrics(df_cv, rolling_window=1)
                rmses.append(df_p['rmse'].values[0])

            best_params = all_params[np.argmin(rmses)]

            if len(rmses) > 0:
                self.db.put_prophet_params(self.stock, self.model_name, best_params)

            self._model = fitted_models[
                hashlib.md5(json.dumps(best_params, sort_keys=True).encode('utf-8')).hexdigest()
            ]
        else:
            model = self.get_prophet_model(hyperparameters, extra_features)

            model.fit(self.data.data)

            self._model = model

        return self._model

    def predict(
            self,
            data_loader: Optional[DataLoader] = None,
            all_data: bool = False,
            periods: int = None,
            extra_features: dict = None
    ) -> DataFrame:
        assert self._model is not None

        prediction = self._model.make_future_dataframe(periods=periods, include_history=False)

        prediction_no_weekdays = prediction[prediction['ds'].dt.dayofweek < 5]

        if extra_features is not None:
            for feature in extra_features.keys():
                extra_features[feature].drop(extra_features[feature].columns.difference(['ds', 'yhat']), 1,
                                             inplace=True)
                extra_features[feature].rename(columns={"yhat": feature}, inplace=True)
                prediction_no_weekdays = pd.merge(prediction_no_weekdays, extra_features[feature], on='ds')

        return self._model.predict(prediction_no_weekdays)

    def tune(self) -> None:
        pass

    def execute_prediction(self, data: pd.DataFrame, name: str = "test") -> pd.DataFrame:
        pass
