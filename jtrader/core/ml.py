from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from dask.distributed import Worker, Scheduler

import jtrader.core.machine_learning as ml
from jtrader.core.provider import IEX

API_RESULT_FOLDER = 'provider_data'
PREDICTION_FOLDER = 'predictions'
ALGORITHMS = [
    'linear-learner'
]


class ML:
    def __init__(self, iex_provider: IEX):
        self.client = iex_provider

    @staticmethod
    def start_dask_worker(
            address: str,
            listen_address: str,
            listen_address_port: int,
            contact_address: str | None = None
    ):
        async def f():
            w = await Worker(
                address,
                contact_address=contact_address,
                host=listen_address,
                port=listen_address_port
            )
            await w.finished()

        asyncio.get_event_loop().run_until_complete(f())

    @staticmethod
    def start_dask_scheduler():
        async def f():
            s = Scheduler(port=8786)
            s = await s
            await s.finished()

        asyncio.get_event_loop().run_until_complete(f())

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
            dask_cluster_address: str = None,
            timeframe: str = '5y'
    ):
        periods = 60

        if with_numerai:
            raise NotImplementedError()
        else:
            predictions = {}
            feature_training_data = {}
            api_result = None
            for data_type in self.client.IEX_TRAINABLE_DATA_POINTS.keys():
                for indicator_name in self.client.IEX_TRAINABLE_DATA_POINTS[data_type]:
                    is_stock_specific_param = True
                    api_result_name = f"{stock}_{indicator_name}_{timeframe}"
                    prediction_save_name = f"prediction_{stock}_{indicator_name}_{periods}"

                    if data_type == self.client.IEX_DATA_TYPE_ECONOMICS:
                        api_result_name = f"{indicator_name}_{timeframe}"
                        prediction_save_name = f"prediction_{indicator_name}_{periods}"
                        is_stock_specific_param = False

                    api_result = self.load_api_result(api_result_name)

                    if api_result is None:
                        print(f"creating new api result for {indicator_name} indicator...")

                        if data_type == self.client.IEX_DATA_TYPE_INDICATOR:
                            api_result = self.client.technicals(
                                stock,
                                indicator_name,
                                timeframe,
                                True
                            ).sort_values(by='date', ascending=True)
                        elif data_type == self.client.IEX_DATA_TYPE_ECONOMICS:
                            api_result = self.client.economic(
                                indicator_name,
                                timeframe,
                                True
                            ).sort_values(by='date', ascending=True)
                        else:
                            raise RuntimeError

                        self.save_api_result(api_result, api_result_name)

                    api_result.drop(
                        [
                            'symbol',
                            'label',
                            'subkey',
                            'updated',
                            'key',
                            'id',
                        ],
                        axis=1,
                        inplace=True,
                        errors='ignore'
                    )

                    if indicator_name in self.client.SPECIAL_INDICATORS:
                        indicator_name = self.client.SPECIAL_INDICATORS[indicator_name]

                    indicator_data = api_result.iloc[:, api_result.columns.get_loc(indicator_name):]

                    if True in indicator_data.isnull().all().values or indicator_data[indicator_name].sum() == 0:
                        continue

                    feature_training_data[indicator_name] = indicator_data

                    prediction_result = self.load_prediction_result(prediction_save_name)

                    if prediction_result is None:
                        data = api_result.copy()
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
                                model_name=indicator_name,
                                is_stock_specific=is_stock_specific_param
                            )

                            local_trainer.train(dask_cluster_address=dask_cluster_address)

                            prediction_result = local_trainer.predict(periods=periods)

                            self.save_prediction_result(prediction_result, prediction_save_name)

                    predictions[indicator_name] = prediction_result

            if api_result is None:
                print('API result missing')

                return

            final_prediction_data = pd.DataFrame(
                {
                    "ds": api_result.index,
                    "y": api_result['close']
                }
            )

            final_prediction_data['ds'] = pd.to_datetime(final_prediction_data['ds'])
            final_prediction_data.reset_index(level=0, drop=True, inplace=True)

            data_loader = ml.local.LocalDataLoader([], data=final_prediction_data)
            local_trainer = ml.local.LocalLinearLearner(
                data=data_loader,
                stock=stock,
                timeframe=timeframe,
                model_name='close'
            )

            local_trainer.train(
                dask_cluster_address=dask_cluster_address,
                extra_features=feature_training_data
            )

            prediction = local_trainer.predict(periods=periods, extra_features=predictions)

            prediction.to_csv(
                'pred.csv',
                columns=['ds', 'trend', 'additive_terms', 'multiplicative_terms', 'yhat'],
                header=['date', 'trend', 'additive_terms', 'multiplicative_terms', 'prediction'],
                index=False
            )

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
