import hashlib
import itertools
import json
from pathlib import Path
from typing import Union, Optional

import numpy as np
import pandas as pd
from fbprophet import Prophet
from fbprophet.diagnostics import cross_validation, performance_metrics
from pandas import DataFrame

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

    # this needs to be DB driven
    hyperparams = {
        "MSFT": {
            "abs": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "ad": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "add": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "adosc": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "ao": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "additive"
            },
            "apo": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "aroon_up": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "aroonosc": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "atan": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "atr": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "avgprice": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "bbands_upper": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "bop": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "cci": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "ceil": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "cmo": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "cosh": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "cvi": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "decay": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "dema": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "dop": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "dx": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "edecay": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "ema": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "emv": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "exp": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "fisher": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "fosc": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "hma": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "kama": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "kvo": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "lag": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "linreg": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "linregintercept": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "linregslope": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "ln": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "additive"
            },
            "log10": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 10,
                "seasonality_mode": "additive"
            },
            "macd": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 10,
                "seasonality_mode": "additive"
            },
            "mass": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "matr": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "max": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "md": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "medprice": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "mfi": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "min": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "mom": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "msw_lead": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "mul": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "nvi": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "obv": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "ppo": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "psar": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "pvi": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "qstick": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "radians": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "roc": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "rocr": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "round": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "rsi": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "sin": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "sinh": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "sma": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "sqrt": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "stddev": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "stderr": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "stochrsi": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "stock_k": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "sum": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "tan": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "tema": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "tr": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "trima": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "trix": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
            "trunc": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "tsf": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "typprice": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "ultosc": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "var": {
                "changepoint_prior_scale": 0.001,
                "seasonality_prior_scale": 0.1,
                "seasonality_mode": "multiplicative"
            },
            "vhf": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "vidya": {
                "changepoint_prior_scale": 0.5,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "volatility": {
                "changepoint_prior_scale": 0.01,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "multiplicative"
            },
            "vosc": {
                "changepoint_prior_scale": 0.1,
                "seasonality_prior_scale": 0.01,
                "seasonality_mode": "additive"
            },
        }
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
                    data = pd.merge(self.data.data, df, on='ds')
                    data[feature].fillna(data[feature].mean(), inplace=True)
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
            extra_features: Optional[dict] = None
    ) -> Prophet:
        if hyperparameters is None or len(hyperparameters) == 0:
            hyperparameters = self.db.get_prophet_params(self.stock, self.model_name)

        # if there are no hyperparameters provided, run auto-tuning
        if hyperparameters is None:
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

                df_cv = cross_validation(model, horizon='30 days', parallel="processes")
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
            for prediction_name in extra_features.keys():
                prediction[prediction_name] = extra_features[prediction_name]

        return self._model.predict(prediction_no_weekdays)

    def tune(self) -> None:
        pass

    def execute_prediction(self, data: pd.DataFrame, name: str = "test") -> pd.DataFrame:
        pass
