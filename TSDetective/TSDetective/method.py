import numpy as np
from collections.abc import Iterable
from statsforecast.models import AutoARIMA
from statsmodels.tsa.seasonal import MSTL


# Base Transformation Class
class Transformation:
    def transform(self, series):
        """Transform the input time series."""
        raise NotImplementedError("Subclasses must implement the transform method.")


# AddN Transformation
class AddN(Transformation):
    def __init__(self, n):
        self.n = n

    def transform(self, series):
        return series + self.n

# MultiplyN Transformation
class MultiplyN(Transformation):
    def __init__(self, n):
        self.n = n

    def transform(self, series):
        return series * self.n

# SubN Transformation
class SubN(Transformation):
    def __init__(self, n):
        self.n = n

    def transform(self, series):
        return series - self.n

# Flip Transformation
class Flip(Transformation):
    def __init__(self):
        pass

    def transform(self, series):
        flipped = series * -1
        flipped += np.abs(np.min(flipped)) + np.min(series)
        return flipped

class ResidualFlip(Transformation):
    def __init__(self, seasonal_period=12):
        self.seasonal_period = seasonal_period

    def transform(self, series):
        """
        Use MSTL to extract the trend from the series, calculate residuals,
        flip the residuals, and reconstruct the series.
        """
        # Apply MSTL decomposition
        mstl = MSTL(series, periods=self.seasonal_period)
        decomposition = mstl.fit()
        trend = decomposition.trend  # Extract the trend component
        residuals = series - trend   # Calculate residuals

        # Flip residuals and reconstruct the series
        flipped_residuals = -residuals
        transformed_series = trend + flipped_residuals
        return transformed_series


# Main Class for Analysis
class Detective:
    def __init__(self, original_series, transformations, holdout_length, seasonality):
        """
        Initialize the TSDetective with the original series, transformations, holdout set size, and seasonality.
        """
        self.original_series = original_series
        self.transformations = transformations
        self.holdout_length = holdout_length
        self.seasonality = seasonality
        self.transformed_series_split = None

    def generate_transformed_series(self):
        """
        Apply transformations and split the transformed series into training and holdout sets.
        Returns:
            transformed_series_split (list of dict): A list where each element is a dictionary with:
                - "train": Transformed training series
                - "holdout": Transformed holdout series
        """
        train_length = len(self.original_series) - self.holdout_length
        self.transformed_series_split = [
            {
                "train": transform.transform(self.original_series)[:train_length],
                "holdout": transform.transform(self.original_series)[train_length:]
            }
            for transform in self.transformations
        ]
        return self.transformed_series_split

    def fit_autoarima_and_predict(self, series):
        """Fit an AutoARIMA model and return the forecast mean."""
        model = AutoARIMA(season_length=self.seasonality)
        model.fit(series)
        predictions = model.predict(self.holdout_length)
        return predictions['mean']

    def compute_autoarima_error_ratios(self):
        """Compute error ratios using AutoARIMA for the original and transformed series."""
        if self.transformed_series_split is None:
            self.generate_transformed_series()

        train_length = len(self.original_series) - self.holdout_length
        train_original = self.original_series[:train_length]
        holdout_original = self.original_series[train_length:]
        original_predictions = self.fit_autoarima_and_predict(train_original)

        ratios = []
        for split in self.transformed_series_split:
            transformed_train = split["train"]
            transformed_holdout = split["holdout"]
            transformed_predictions = self.fit_autoarima_and_predict(transformed_train)

            original_error = 100 * np.mean(np.abs(original_predictions - holdout_original))/np.abs(np.mean(holdout_original))
            transformed_error = 100 * np.mean(np.abs(transformed_predictions - transformed_holdout))/np.abs(np.mean(transformed_holdout))
            ratios.append(original_error / transformed_error)

        return ratios

    def compute_foundation_model_error_ratios(self, foundation_errors_original, foundation_errors_transformed):
        """Compute ratios between original and transformed series errors for the foundation model."""
        if isinstance(foundation_errors_transformed, Iterable):
            return [
                original_error / transformed_error
                for original_error, transformed_error in zip(foundation_errors_original, foundation_errors_transformed)
            ]
        else:
            return [foundation_errors_original / foundation_errors_transformed]

    def compare_error_ratios(self, autoarima_ratios, foundation_ratios):
        """Compare AutoARIMA error ratios with foundation model error ratios."""
        if isinstance(autoarima_ratios, Iterable):
            return [
                autoarima_ratio / foundation_ratio
                for autoarima_ratio, foundation_ratio in zip(autoarima_ratios, foundation_ratios)
            ]
        else:
            return (autoarima_ratios) / (foundation_ratios)

    @staticmethod
    def calculate_nmse(predictions, holdout):
        """
        Calculate the Normalized Mean Squared Error (MSE) between predictions and the actual holdout values.
        Args:
            predictions (array-like): Predicted values.
            holdout (array-like): Actual holdout values.
        Returns:
            float: The MSE value.
        """
        mse = 100 * np.mean((np.array(predictions) - np.array(holdout)) ** 2)/np.abs(np.mean(holdout))
        return mse
