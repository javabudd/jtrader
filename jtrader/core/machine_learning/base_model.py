import logging
from abc import ABC, abstractmethod
from typing import Optional, Union

from pandas import DataFrame

from .data_loader import DataLoader

LOGGER = logging.getLogger(__name__)


class BaseModel(ABC):
    def __init__(self, data: DataLoader, model_name: str = None) -> None:
        self.data = data
        self.model_name = model_name

    @abstractmethod
    def train(
            self,
            hyperparameters: Optional[dict] = None,
            extra_features: Optional[dict] = None,
            with_dask: Optional[bool] = False
    ) -> Union[None, object]:
        """
        Trains the model, with the data provided
        """
        pass

    @abstractmethod
    def load_model(self) -> None:
        """
        Load the already trained model to not have to train again.
        """
        pass

    @abstractmethod
    def execute_prediction(self, data: DataFrame, name: str = "test") -> DataFrame:
        """
        Actually executes the predictions. Based on implementation

        Arguments:
            data: The data to predict
            name: Name of model

        Return:
            The predictions in a dataframe
        """
        pass

    @abstractmethod
    def tune(self) -> None:
        """
        Tunes the current models with the provided hyperparameter tuning dict.
        """
        pass

    def predict(
            self,
            data_loader: Optional[DataLoader] = None,
            all_data: bool = False,
            periods: int = None,
            extra_features: Union[dict, list] = None
    ) -> DataFrame:
        """
        Predict based on an already trained model.

        Arguments:
            data_loader: The data to predict. If not provided, it will default to the local data loader.
            all_data: Whether to predict all the data in the data loader. If false, the test data will be predicted.
            periods: Numer of periods to predict (optional)
            extra_features: Features to merge with the prediction data set (optional)
        """
        if data_loader is None:
            data_loader = self.data

        if all_data:
            data = data_loader.data
            name = "predict"
        else:
            data = data_loader.test_data
            name = "test"

        x_test = data.loc[:, data_loader.feature_columns]

        return data_loader.format_predictions(
            self.execute_prediction(x_test, name),
            all_data=all_data
        )
