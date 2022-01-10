from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

import jtrader.core.machine_learning as ml
from jtrader.core.provider.iex import IEX

API_RESULT_FOLDER = 'provider_data'
PREDICTION_FOLDER = 'predictions'
ALGORITHMS = [
    'linear-learner'
]


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
    def save_prediction_result(prediction, name) -> None:
        try:
            Path(PREDICTION_FOLDER).mkdir(exist_ok=True, parents=True)
        except Exception as ex:
            pass
        pd.to_pickle(prediction, f"{PREDICTION_FOLDER}/{name}.pkl")

    @staticmethod
    def load_api_result(name) -> Union[None, pd.DataFrame]:
        path = Path(f"{API_RESULT_FOLDER}/{name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{API_RESULT_FOLDER}/{name}.pkl")
        else:
            model = None
        return model

    @staticmethod
    def load_prediction_result(name) -> Union[None, pd.DataFrame]:
        path = Path(f"{PREDICTION_FOLDER}/{name}.pkl")
        if path.is_file():
            prediction = pd.read_pickle(f"{PREDICTION_FOLDER}/{name}.pkl")
        else:
            prediction = None
        return prediction

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

    def run_trainer(
            self,
            stock: str,
            training_algorithm: str,
            with_aws: bool = False,
            with_numerai: bool = False,
            timeframe: str = '5y'
    ):
        periods = 60

        if with_numerai:
            data_loader = ml.numerai.NumeraiDataLoader(local_data_location="training_data.parquet")
        else:
            predictions = {}
            feature_training_data = {}
            final_prediction_data = None
            api_result = None
            for indicator_name in self.client.IEX_TECHNICAL_INDICATORS:
                api_result_name = f"{stock}_{indicator_name}_{timeframe}"
                prediction_save_name = f"prediction_{stock}_{indicator_name}_{periods}"

                prediction_result = self.load_prediction_result(prediction_save_name)

                api_result = self.load_api_result(api_result_name)

                if api_result is None:
                    print(f"creating new api result for {indicator_name} indicator...")

                    data = self.client.technicals(
                        stock,
                        indicator_name,
                        timeframe, True
                    ).sort_values(by='date', ascending=True)

                    self.save_api_result(data, api_result_name)
                else:
                    data = api_result

                data.drop(
                    [
                        'symbol',
                        'label',
                        'subkey',
                        'updated',
                        'key',
                        'id',
                    ],
                    axis=1,
                    inplace=True
                )

                if indicator_name in self.client.SPECIAL_INDICATORS:
                    indicator_name = self.client.SPECIAL_INDICATORS[indicator_name]

                indicator_data = data.iloc[:, data.columns.get_loc(indicator_name):]

                if True in indicator_data.isnull().all().values:
                    continue

                feature_training_data[indicator_name] = indicator_data

                if prediction_result is None:
                    data.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
                    data.reset_index(level=0, inplace=True)
                    data.rename(columns={"date": "ds", indicator_name: "y"}, inplace=True)
                    data_loader = ml.local.LocalDataLoader([], data=data)

                    if with_aws:
                        sagemaker = ml.aws.Sagemaker()
                        linear = ml.aws.LinearAwsLinearLearner(data=data_loader, aws_executor=sagemaker)

                        linear.train()
                    else:
                        local_trainer = ml.local.LocalLinearLearner(
                            data=data_loader,
                            stock=stock,
                            timeframe=timeframe,
                            model_name=indicator_name
                        )

                        hyperparams = {}
                        if indicator_name in ml.local.LocalLinearLearner.hyperparams:
                            hyperparams = ml.local.LocalLinearLearner.hyperparams[indicator_name]

                        local_trainer.train(hyperparameters=hyperparams)

                        prediction_result = local_trainer.predict(periods=periods)

                        self.save_prediction_result(prediction_result, prediction_save_name)

                        if final_prediction_data is None:
                            final_prediction_data = pd.DataFrame(
                                {"ds": data['ds'], "y": data['close']}
                            )

                predictions[indicator_name] = prediction_result['yhat']

            if api_result is None:
                print('API result missing')

            if final_prediction_data is None:
                api_result.reset_index(level=0, inplace=True)
                final_prediction_data = pd.DataFrame(
                    {"ds": api_result['date'], "y": api_result['close']}
                )

            data_loader = ml.local.LocalDataLoader([], data=final_prediction_data)
            local_trainer = ml.local.LocalLinearLearner(
                data=data_loader,
                stock=stock,
                timeframe=timeframe,
                model_name='close'
            )

            local_trainer.train(extra_features=feature_training_data)

            prediction = local_trainer.predict(periods=periods, extra_features=predictions)

            prediction.to_csv('pred.csv')

    def run_predictor(self, model_name: str, prediction: list) -> None:
        model = self.load_model(model_name)

        if model is None:
            print('can not load given model')
            return

        prediction = model.make_future_dataframe(periods=365, include_history=False)

        print(
            {
                "Prediction": model.predict(prediction)
            }
        )
