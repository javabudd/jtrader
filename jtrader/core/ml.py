from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd

import jtrader.core.machine_learning as ml
from jtrader.core.provider.iex import IEX

API_RESULT_FOLDER = 'provider_data'
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
    def load_api_result(name) -> Union[None, pd.DataFrame]:
        path = Path(f"{API_RESULT_FOLDER}/{name}.pkl")
        if path.is_file():
            model = pd.read_pickle(f"{API_RESULT_FOLDER}/{name}.pkl")
        else:
            model = None
        return model

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
        if with_numerai:
            data_loader = ml.numerai.NumeraiDataLoader(local_data_location="training_data.parquet")
        else:
            combined = pd.DataFrame()
            for indicator_name in self.client.IEX_TECHNICAL_INDICATORS:
                api_result_name = f"{stock}_{indicator_name}_{timeframe}"

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

                if len(combined) == 0:
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
                    combined = data
                else:
                    if indicator_name in self.client.SPECIAL_INDICATORS:
                        indicator_name = self.client.SPECIAL_INDICATORS[indicator_name]

                    combined = pd.concat([combined, data[indicator_name].astype('float32')], axis=1)

            combined.replace([np.inf, -np.inf, np.nan], 0, inplace=True)
            combined.sort_index(inplace=True, ascending=True)
            combined.reset_index(level=0, inplace=True)
            combined['date'] = combined['date'].astype(np.int64) / 1000000

            combined.rename(columns={"date": "ds", "close": "y"}, inplace=True)

            data_loader = ml.local.LocalDataLoader([], data=combined)

        if with_aws:
            sagemaker = ml.aws.Sagemaker()
            linear = ml.aws.LinearAwsLinearLearner(data=data_loader, aws_executor=sagemaker)

            linear.train()
        else:
            local_trainer = ml.local.LocalLinearLearner(
                data=data_loader,
                stock=stock,
                timeframe=timeframe
            )

            local_trainer.train()

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
