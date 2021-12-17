from pathlib import Path

import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

API_RESULT_FOLDER = 'data'
MODEL_FOLDER = 'models'


class ML():
    @staticmethod
    def save_api_result(api_result, name):
        try:
            Path(API_RESULT_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(api_result, f"{API_RESULT_FOLDER}/{name}.pkl")

    @staticmethod
    def load_api_result(name):
        path = Path(f"{API_RESULT_FOLDER}/{name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{API_RESULT_FOLDER}/{name}.pkl")
        else:
            model = False
        return model

    @staticmethod
    def save_model(model, name):
        try:
            Path(MODEL_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(model, f"{MODEL_FOLDER}/{name}.pkl")

    @staticmethod
    def load_model(name):
        path = Path(f"{MODEL_FOLDER}/{name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{MODEL_FOLDER}/{name}.pkl")
        else:
            model = False
        return model

    def optimize_machine_learning_params(self):
        # optuna
        pass

    def run_machine_learning(self):
        indicators = {
            'abs': 'abs',
            'acos': 'acos',
            'ad': 'ad',
            'add': 'add',
            'ema': 'ema'
        }

        params = {
            # "boosting_type": "goss",
            # "n_estimators": 1842,
            # "learning_rate": 0.026520287506337205,
            # "num_leaves": 6,
            # "max_depth": 5,
            # "feature_fraction": 0.10866666339142045,
            # "bagging_fraction": 0.0178426564762887,
            # "min_data_in_leaf": 270
        }

        ticker = 'MSFT'
        indicator_name = indicators['ema']
        timeframe = '5y'

        api_result_name = f"{ticker}_{indicator_name}_{timeframe}"

        api_result = self.load_api_result(api_result_name)

        if not api_result:
            print('creating new api result...')

            data = self.client.stocks.technicalsDF(
                'MSFT',
                indicator_name,
                range=timeframe
            ).sort_values(by='date', ascending=True)

            self.save_api_result({"data": data}, api_result_name)
        else:
            data = api_result['data']

        model_name = f"{ticker}_{indicator_name}_{timeframe}"

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

        if not model:
            print('creating new model...')

            model = LinearRegression(**params)

            model.fit(x_train, y_train)

            self.save_model(model, model_name)

        predicted_test_data = model.predict(x_test)

        absolute_error = metrics.mean_absolute_error(y_test, predicted_test_data)
        mean_squared_error = metrics.mean_squared_error(y_test, predicted_test_data)
        r_squared = metrics.r2_score(y_test, predicted_test_data)

        prediction = [
            [324.9, 35034831]
        ]

        print(
            {
                "Absolute Error": absolute_error,
                "Mean Squared Error": mean_squared_error,
                "R Squared": r_squared,
                "Prediction": model.predict(prediction)
            }
        )
