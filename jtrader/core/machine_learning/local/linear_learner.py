from pathlib import Path
from typing import Union

import pandas as pd
from sklearn.linear_model import LinearRegression

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

    def train(self) -> None:
        y_train = self.data.train_data.loc[:, self.data.output_column]
        x_train = self.data.train_data.loc[:, self.data.feature_columns]

        model_name = f"{self.stock}_{self.name}_{self.timeframe}"

        model = self.load_model(model_name)

        if not model:
            print('creating new model...')

            model = LinearRegression(**{})

            model.fit(x_train, y_train)

            self.save_model(model, model_name)

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
        print('asdf')
        exit()
        return pd.DataFrame(self._model.predict(data))
