import numpy as np
from pandas import DataFrame

from jtrader.core.machine_learning.data_loader import DataLoader


class LocalDataLoader(DataLoader):
    index_column = "id"
    data_type_column = "data_type"
    time_column = "date"
    output_column = "close"

    def __init__(self, feature_columns: list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.feature_columns = feature_columns

    def format_predictions(
            self, y_pred: DataFrame, all_data: bool = False
    ) -> DataFrame:
        """
        Formats the predictions by setting index and columns

        Arguments:
            y_pred: dataframe with the predictions
            all_data: whether all data was used

        Returns:
            The formatted DataFrame
        """
        if all_data:
            y_labels = self.data
        else:
            y_labels = self.test_data
        # Format index and columns
        y_pred = y_pred.set_index(y_labels.index, inplace=False)
        output_columns = [
            column.replace(self.output_column, "prediction") for column in [self.output_column]
        ]
        y_pred = y_pred.set_axis(output_columns, axis=1, inplace=False)
        return y_pred

    def score(self, y_pred: DataFrame, all_data: bool = False) -> float:
        """
        Scores the data versus the predictions.
        For numerai, corretation coefficient is used.

        Arguments:
            y_pred: the predicted values
            all_data: Whether to use the complete dataset to compare to, or just the test set

        Returns:
            The scoring metric (correlation coefficient)
        """
        if all_data:
            y_labels = self.data
        else:
            y_labels = self.test_data
        y_labels = y_labels.loc[:, self.output_column]
        metric = self.execute_scoring(y_labels, y_pred)
        return metric

    @staticmethod
    def execute_scoring(labels: DataFrame, prediction: DataFrame) -> float:
        """
        Scores the correlation as defined by the Numerai tournament rules.

        Arguments:
            labels: The real labels of the output
            prediction: The predicted labels

        Returns:
            The correlation coefficient
        """
        ranked_prediction = prediction.rank(pct=True, method="first")
        return np.corrcoef(labels, ranked_prediction, rowvar=False)[0, 1]
