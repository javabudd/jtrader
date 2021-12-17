from pathlib import Path
from typing import Union

import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from jtrader.core.provider.iex import IEX

API_RESULT_FOLDER = 'data'
MODEL_FOLDER = 'models'


class ML:
    def __init__(self, iex_provider: IEX):
        self.client = iex_provider

    @staticmethod
    def save_api_result(api_result, name) -> None:
        try:
            Path(API_RESULT_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(api_result, f"{API_RESULT_FOLDER}/{name}.pkl")

    @staticmethod
    def load_api_result(name) -> Union[None, pd.DataFrame]:
        path = Path(f"{API_RESULT_FOLDER}/{name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{API_RESULT_FOLDER}/{name}.pkl")
        else:
            model = None
        return model

    @staticmethod
    def save_model(model, name: str) -> None:
        try:
            Path(MODEL_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(model, f"{MODEL_FOLDER}/{name}.pkl")

    @staticmethod
    def load_model(name: str) -> Union[None, pd.DataFrame]:
        path = Path(name)
        if path.is_file():
            model = pd.read_pickle(f"{name}")
        else:
            model = None
        return model

    def optimize_machine_learning_params(self) -> None:
        # optuna
        pass

    def run_trainer(self, stock: str, indicator_name: str, timeframe: str = '5y'):
        api_result_name = f"{stock}_{indicator_name}_{timeframe}"

        api_result = self.load_api_result(api_result_name)

        if api_result is None:
            print('creating new api result...')

            data = self.client.technicals(
                stock,
                indicator_name,
                timeframe, True
            ).sort_values(by='date', ascending=True)

            self.save_api_result(data, api_result_name)
        else:
            data = api_result

        model_name = f"{stock}_{indicator_name}_{timeframe}"

        model = self.load_model(indicator_name)

        training_columns = [
            indicator_name,
            'volume'
        ]

        x_train, x_test, y_train, y_test = train_test_split(
            data[training_columns].values,
            data['close'].values,
            test_size=0.2,
            random_state=0
        )

        if model is None:
            print('creating new model...')

            model = LinearRegression(**{})

            model.fit(x_train, y_train)

            self.save_model(model, model_name)

        predicted_test_data = model.predict(x_test)

        absolute_error = metrics.mean_absolute_error(y_test, predicted_test_data)
        mean_squared_error = metrics.mean_squared_error(y_test, predicted_test_data)
        r_squared = metrics.r2_score(y_test, predicted_test_data)

        print(
            {
                "Model": model_name,
                "Absolute Error": absolute_error,
                "Mean Squared Error": mean_squared_error,
                "R Squared": r_squared
            }
        )

    def run_machine_learning(self, model_name: str, prediction: list) -> None:
        model = self.load_model(model_name)

        if model is None:
            print('can not load given model')
            return

        print(
            {
                "Prediction": model.predict(prediction)
            }
        )
