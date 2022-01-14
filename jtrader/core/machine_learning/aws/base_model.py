import logging
import os
import gc
from abc import ABC
from typing import Dict, Optional, Union, Any

import pandas as pd
from pandas import DataFrame
from sagemaker import TrainingInput
from sagemaker.amazon.amazon_estimator import get_image_uri
from sagemaker.estimator import Estimator
from sagemaker.predictor import RealTimePredictor
from sagemaker.transformer import Transformer
from sagemaker.tuner import HyperparameterTuner

from jtrader.core.machine_learning.base_model import BaseModel
from jtrader.core.machine_learning.data_loader import DataLoader
from .executor.sagemaker import Sagemaker

LOGGER = logging.getLogger(__name__)


class AwsBase(BaseModel, ABC):
    default_hyperparameters = NotImplemented
    name = "aws-base"

    def __init__(
            self,
            data: DataLoader,
            aws_executor: Sagemaker,
            output_path: Optional[str] = None,
            local_save_folder: Optional[str] = None,
    ) -> None:
        """
        Initializes a general AWS model with data and an executor.
        This will not yet do any training or data uploading.
        """
        super().__init__(data)

        self.executor = aws_executor
        self.model_name = None
        self.prefix = f"{self.executor.prefix}/{self.name}"
        self.input_data_prefix = f"{self.prefix}/input_data"
        self.output_data_prefix = f"{self.prefix}/output_data"

        if output_path is not None:
            self.output_path = output_path
        else:
            self.output_path = "s3://{bucket}/{prefix}".format(
                bucket=self.executor.bucket, prefix=self.output_data_prefix
            )
        if local_save_folder is not None:
            self.local_save_folder = local_save_folder
        else:
            self.local_save_folder = f"data/temp/{self.name}"

    def prepare_data(
            self,
            data_name: str,
            x_data: Optional[DataFrame] = None,
            y_data: Optional[DataFrame] = None,
            s3_input_type: bool = True,
            s3_item: Optional[str] = None
    ) -> Union[TrainingInput, str]:
        """
        Prepares the data to use in the learner.

        Arguments:
            data_name: name of data
            x_data: the features of the data
            y_data: (optional) the output of the data. Don't provide for predictions
            s3_input_type: (optional) s3 bucket
            s3_item: (optional) item in s3, overrides all logic here

        Returns:
            The s3 input or s3 location of the data
        """
        LOGGER.info("Preparing data for usage")

        if s3_item:
            if s3_input_type:
                return TrainingInput(s3_item, content_type="text/csv")

            return s3_item

        # Try to get from cache
        return_data = None
        if data_name != "predict":
            return_data = self.data.get_from_cache("s3", data_name)
        if return_data is not None:
            LOGGER.info("Found s3 data in cache.")
            if s3_input_type:
                return TrainingInput(return_data, content_type="text/csv")
            return return_data

        # Try to get local data from cache
        temp_location = None
        if data_name != "predict":
            temp_location = self.data.get_from_cache("local", data_name)
        # If not available, save to local
        if temp_location is None:
            if not os.path.exists(self.local_save_folder):
                os.makedirs(self.local_save_folder)
            temp_location = f"{self.local_save_folder}/{data_name}.csv"
            if y_data is not None:
                data = pd.concat([y_data, x_data], axis=1)
            else:
                data = x_data
            LOGGER.info("Writing data to local machine")
            data.to_csv(temp_location, index=False, header=False)
        else:
            # Log if present
            LOGGER.info("Found local data location in cache.")

        # Upload to S3
        return_data = self.executor.upload_data(
            temp_location, prefix=self.input_data_prefix
        )
        # Put in cache
        if data_name != "predict":
            self.data.add_to_cache("s3", data_name, return_data)

        if s3_input_type:
            return_data = TrainingInput(return_data, content_type="text/csv")

        return return_data

    def _load_results(self, file_name: str) -> DataFrame:
        # Add S3 results to cache
        prediction_file_name = f"{file_name}.csv.out"
        s3_location = f"s3://{self.executor.bucket}/{self.output_data_prefix}/{prediction_file_name}"
        self.data.add_to_cache("s3", "test_predictions", s3_location)

        # Download from S3
        local_file_location = self.executor.download_data(
            prediction_file_name, self.local_save_folder, prefix=self.output_data_prefix
        )
        # Add local files to cache
        self.data.add_to_cache("local", "test_predictions", local_file_location)

        # Load dataframe and put in cache
        df = pd.read_csv(local_file_location, header=None)
        df.index = list(df.index)
        self.data.add_to_cache("dataframe", "test_predictions", df)

        return df

    def get_s3_input_data(
            self,
            training_data_location: Union[None, str] = None,
            validation_data_location: Union[None, str] = None
    ) -> list:
        if training_data_location is not None:
            s3_input_train = self.prepare_data("train", None, None, True, training_data_location)
        else:
            y_train = self.data.train_data.loc[:, self.data.output_column]
            x_train = self.data.train_data.loc[:, self.data.feature_columns]
            s3_input_train = self.prepare_data("train", x_train, y_train)

        if validation_data_location:
            s3_input_validation = self.prepare_data("validation", None, None, True, validation_data_location)
        else:
            y_validation = self.data.validation_data.loc[:, self.data.output_column]
            x_validation = self.data.validation_data.loc[:, self.data.feature_columns]
            s3_input_validation = self.prepare_data(
                "validation",
                x_validation,
                y_validation,
                True,
                validation_data_location
            )

        return [s3_input_train, s3_input_validation]


class AwsEstimator(AwsBase, ABC):
    """
    The general implementation of a AWS Estimator model:
    https://sagemaker.readthedocs.io/en/stable/estimators.html
    https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html

    This is an abstract class. Please subclass it and set the following class parameters:
        * container_name
        * default_hyperparameters
        * name
    """

    default_hyperparameters = {}
    default_hyperparameter_tuning = {}
    default_tuning_job_config = {
        "max_jobs": 3,
        "max_parallel_jobs": 3,
        "objective_metric_name": "validation:rmse",
        "objective_type": "Minimize",
    }
    container_name = NotImplemented
    name = "aws-estimator"

    def __init__(
            self,
            data: DataLoader,
            aws_executor: Sagemaker,
            output_path: Optional[str] = None,
            local_save_folder: Optional[str] = None,
    ) -> None:
        """
        Initializes a AWS Estimator with data and an executor.
        This will not yet do any training or data uploading.
        """
        LOGGER.info(f"Initializing AWS Estimator {self.name} model")

        super().__init__(data, aws_executor, output_path, local_save_folder)

        self._model: Estimator = None
        self._transformer: Transformer = None
        self._predictor: RealTimePredictor = None
        self._tuner: HyperparameterTuner = None

    def train(
            self,
            hyperparameters: Dict = {},
            extra_features: Optional[dict] = {},
            dask_cluster_address: Optional[str] = None
    ) -> None:
        """
        Trains the model, with the data provided

        Arguments:
            hyperparameters: The hyperparameters to provide to the Estimator model.
                See https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html
                And specific implementations
            extra_features: Extra features to train against
            dask_cluster_address: With dask cluster
        """
        LOGGER.info("Starting to train model.")
        self._model = self._get_model(hyperparameters)

        train, validation = self.get_s3_input_data()

        gc.collect()

        LOGGER.info("Starting to fit model")
        self._model.fit({"train": train, "validation": validation})
        LOGGER.info("Done with fitting model")

    def _get_model(self, hyperparameters: Dict = {}) -> Estimator:
        """
        Initializes the model. This can be used to train later or attach an existing model

        Arguments:
            hyperparameters: The hyperparameters for the Estimator model

        Returns:
            model: The initialized model
        """
        container = get_image_uri(
            self.executor.boto_session.region_name,
            self.container_name,
            repo_version='1.3-1'
        )
        model = Estimator(
            container,
            **self.executor.default_model_kwargs,
            output_path=self.output_path,
        )
        used_hyperparameters = self.default_hyperparameters
        used_hyperparameters.update(hyperparameters)

        model.set_hyperparameters(**used_hyperparameters)
        return model

    def load_model(self, model_name: str = "") -> None:
        """
        Load the already trained model to not have to train again.

        Arguments:
            model_name: The name of the training job, as provided by AWS
        """
        LOGGER.info(f"Loading already trained model {model_name}")
        self._model = Estimator.attach(
            training_job_name=model_name, sagemaker_session=self.executor.session
        )

    def execute_prediction(self, data: DataFrame, name: str = "test") -> DataFrame:
        """
        Predict based on an already trained model.
        Loads the existing model if it exists.
        Also adds the output data to the cache.

        Arguments:
            data: the data to load. If not provided, is defaulted to the local data
            name: The same of the predictions to save on S3.

        Returns:
            The predicted dataframe
        """
        # Upload to S3
        s3_location_test = self.prepare_data(name, data, s3_input_type=False)

        # Start the job
        LOGGER.info("Creating the transformer job")
        transformer = self._get_transformer()
        transformer.transform(
            s3_location_test, content_type="text/csv", split_type="Line"
        )
        LOGGER.info("Waiting for the transformer job")
        transformer.wait()

        # Download the data
        LOGGER.info("Loading the results of the transformer job")
        y_test = self._load_results(name)

        return y_test

    def _get_transformer(self) -> Transformer:
        """
        Returns a transformer based on the current model
        """
        assert (
                self._model is not None
        ), "Cannot create a transformer if the model is not yet set."
        if self._tuner is not None:
            LOGGER.info("Loading best model from tuning job")
            self.load_model(self._tuner.best_training_job())
        return self._model.transformer(
            **self.executor.default_transformer_kwargs,
            output_path=f"{self.output_path}",
        )

    def tune(
            self,
            tuning_job_parameters: Dict[str, Any] = {},
            hyperparameters: Dict[str, Any] = None,
            hyperparameter_tuning: Dict[str, Any] = None,
            training_data_location: Optional[str] = None,
            validation_data_location: Optional[str] = None
    ) -> None:
        """
        Tunes the current Estimator with the provided hyperparameters
        """
        LOGGER.info("Starting the hyperparameter tuning.")

        if hyperparameters is None:
            hyperparameters = self.default_hyperparameters
        if hyperparameter_tuning is None:
            hyperparameter_tuning = self.default_hyperparameter_tuning
        used_tuning_job_parameters = {
            **self.default_tuning_job_config,
            **tuning_job_parameters,
        }

        if self._model is None:
            self._model = self._get_model(hyperparameters)

        self._tuner = HyperparameterTuner(
            estimator=self._model,
            **used_tuning_job_parameters,
            hyperparameter_ranges=hyperparameter_tuning,
        )

        train, validation = self.get_s3_input_data(training_data_location, validation_data_location)

        LOGGER.info("Starting to tune hyperparameters")
        self._tuner.fit({"train": train, "validation": validation})
        self._tuner.wait()
        LOGGER.info("Done with the tuning job")
