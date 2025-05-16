"""
File: model_training_utils.py
Path: D:/YourProject/src/Utilities/model_training/model_training_utils.py

Description:
    Handles saving, loading, and managing versions of machine learning models.
    Supports different model frameworks (e.g., Keras, scikit-learn) and ensures
    proper storage of models, scalers, and metadata.
    Utilizes a factory-style ModelManager to route to the appropriate specialized manager.
"""

import datetime
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

# Use our new configuration and logging modules.
from config import config
from logger import setup_logging

# Keras imports
from tensorflow.keras.models import Sequential, load_model, save_model


# -----------------------------------------------------------------------------
# Base I/O Class
# -----------------------------------------------------------------------------
class BaseModelIO(ABC):
    """
    Abstract interface for saving/loading models, metadata, and scalers.
    Subclasses must implement the `save_model` and `load_model` methods.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.model_directory = self._get_model_save_dir()

    def _get_model_save_dir(self) -> Path:
        """
        Retrieve the root directory for saving models from config or a default path.
        """
        # You can later extend this to read from config if desired.
        default_path = config.get_env("MODEL_SAVE_PATH", default="SavedModels")
        return Path(default_path)

    @abstractmethod
    def save_model(
        self,
        model,
        symbol: str,
        model_type: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        scaler: Optional[Any] = None,
    ) -> Dict[str, Path]:
        raise NotImplementedError("Subclasses must implement 'save_model'")

    @abstractmethod
    def load_model(
        self, symbol: str, model_type: str, version: Optional[str] = None
    ) -> Optional[Any]:
        raise NotImplementedError("Subclasses must implement 'load_model'")

    def _create_version_directory(self, symbol: str, model_type: str) -> Path:
        """
        Create a timestamped version directory for a given symbol and model type.
        """
        model_dir = self.get_model_directory(symbol, model_type)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        version = f"v_{timestamp}"
        version_dir = model_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        return version_dir

    def get_model_directory(self, symbol: str, model_type: str) -> Path:
        """
        Retrieve the base directory for storing models of a given symbol and type.
        """
        model_dir = self.model_directory / model_type / symbol
        model_dir.mkdir(parents=True, exist_ok=True)
        return model_dir

    def _get_latest_version_dir(self, model_dir: Path) -> Optional[Path]:
        """
        Return the most recently modified version directory within model_dir.
        """
        versions = sorted(
            [d for d in model_dir.iterdir() if d.is_dir()],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        return versions[0] if versions else None

    def _save_metadata(
        self,
        version_dir: Path,
        symbol: str,
        model_type: str,
        model_file: Path,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        timestamp: str,
    ) -> Path:
        """
        Save metadata to a JSON file in the version directory.
        """
        version = version_dir.name
        metadata_file = version_dir / "metadata.json"
        metadata_content = {
            "model_type": model_type,
            "symbol": symbol,
            "model_file": str(model_file),
            "version": version,
            "timestamp": timestamp,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
        }
        try:
            with open(metadata_file, "w") as f:
                json.dump(metadata_content, f, indent=4)
            self.logger.debug(f"Metadata saved at: {metadata_file}")
        except Exception as e:
            self.logger.error(
                f"Failed to save metadata at {metadata_file}: {e}", exc_info=True
            )
            raise
        return metadata_file

    def _load_latest_file(
        self, symbol: str, model_type: str, extension: str, version: Optional[str]
    ) -> Optional[Path]:
        """
        Return the file path for the model or scaler file, either for a specific version or the latest.
        """
        model_dir = self.get_model_directory(symbol, model_type)
        if version:
            version_dir = model_dir / version
            if not version_dir.exists():
                self.logger.error(f"Specified version does not exist: {version_dir}")
                return None
            file_path = list(version_dir.glob(f"*{extension}"))
            return file_path[0] if file_path else None
        else:
            latest_version_dir = self._get_latest_version_dir(model_dir)
            if not latest_version_dir:
                self.logger.error(f"No versions found in directory: {model_dir}")
                return None
            file_path = list(latest_version_dir.glob(f"*{extension}"))
            return file_path[0] if file_path else None


# -----------------------------------------------------------------------------
# Keras Model I/O Implementation
# -----------------------------------------------------------------------------
class KerasModelIO(BaseModelIO):
    """
    Specialized logic for saving and loading Keras (e.g., LSTM, Neural Network) models.
    """

    def save_model(
        self,
        model: Sequential,
        symbol: str,
        model_type: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        scaler: Optional[Any] = None,
    ) -> Dict[str, Path]:
        self.logger.info(f"Saving Keras model: Symbol={symbol}, Type={model_type}")
        version_dir = self._create_version_directory(symbol, model_type)
        model_file = version_dir / f"{symbol}_{model_type}_model.h5"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            save_model(model, model_file)
            self.logger.debug(f"Keras model saved at: {model_file}")
        except Exception as e:
            self.logger.error(
                f"Failed to save Keras model at {model_file}: {e}", exc_info=True
            )
            raise

        scaler_file = None
        if scaler is not None:
            scaler_file = version_dir / f"{symbol}_scaler.pkl"
            try:
                joblib.dump(scaler, scaler_file)
                self.logger.debug(f"Scaler saved at: {scaler_file}")
            except Exception as e:
                self.logger.error(
                    f"Failed to save scaler at {scaler_file}: {e}", exc_info=True
                )
                raise

        metadata_file = self._save_metadata(
            version_dir=version_dir,
            symbol=symbol,
            model_type=model_type,
            model_file=model_file,
            hyperparameters=hyperparameters,
            metrics=metrics,
            timestamp=timestamp,
        )
        self.logger.info(
            f"Saved Keras model for {symbol} at version directory: {version_dir}"
        )
        return {"model": model_file, "scaler": scaler_file, "metadata": metadata_file}

    def load_model(
        self, symbol: str, model_type: str, version: Optional[str] = None
    ) -> Optional[Sequential]:
        self.logger.info(
            f"Loading Keras model: Symbol={symbol}, Type={model_type}, Version={version or 'latest'}"
        )
        model_path = self._load_latest_file(
            symbol, model_type, extension="_model.h5", version=version
        )
        if model_path is None or not model_path.exists():
            self.logger.error(
                f"No Keras model file found for symbol {symbol}, type {model_type}, version {version}"
            )
            return None
        try:
            model = load_model(model_path)
            self.logger.debug(f"Keras model loaded from {model_path}")
            return model
        except Exception as e:
            self.logger.error(
                f"Failed to load Keras model from {model_path}: {e}", exc_info=True
            )
            return None


# -----------------------------------------------------------------------------
# Joblib Model I/O Implementation (for scikit-learn, etc.)
# -----------------------------------------------------------------------------
class JoblibModelIO(BaseModelIO):
    """
    Specialized logic for saving and loading models that can be serialized via joblib.
    (e.g., scikit-learn, XGBoost, LightGBM).
    """

    def save_model(
        self,
        model: Any,
        symbol: str,
        model_type: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        scaler: Optional[Any] = None,
    ) -> Dict[str, Path]:
        self.logger.info(f"Saving Joblib model: Symbol={symbol}, Type={model_type}")
        version_dir = self._create_version_directory(symbol, model_type)
        model_file = version_dir / f"{symbol}_{model_type}_model.pkl"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            joblib.dump(model, model_file)
            self.logger.debug(f"Joblib model saved at: {model_file}")
        except Exception as e:
            self.logger.error(
                f"Failed to save Joblib model at {model_file}: {e}", exc_info=True
            )
            raise

        scaler_file = None
        if scaler is not None:
            scaler_file = version_dir / f"{symbol}_scaler.pkl"
            try:
                joblib.dump(scaler, scaler_file)
                self.logger.debug(f"Scaler saved at: {scaler_file}")
            except Exception as e:
                self.logger.error(
                    f"Failed to save scaler at {scaler_file}: {e}", exc_info=True
                )
                raise

        metadata_file = self._save_metadata(
            version_dir=version_dir,
            symbol=symbol,
            model_type=model_type,
            model_file=model_file,
            hyperparameters=hyperparameters,
            metrics=metrics,
            timestamp=timestamp,
        )
        self.logger.info(
            f"Saved Joblib model for {symbol} at version directory: {version_dir}"
        )
        return {"model": model_file, "scaler": scaler_file, "metadata": metadata_file}

    def load_model(
        self, symbol: str, model_type: str, version: Optional[str] = None
    ) -> Optional[Any]:
        self.logger.info(
            f"Loading Joblib model: Symbol={symbol}, Type={model_type}, Version={version or 'latest'}"
        )
        model_path = self._load_latest_file(
            symbol, model_type, extension="_model.pkl", version=version
        )
        if model_path is None or not model_path.exists():
            self.logger.error(
                f"No Joblib model file found for symbol {symbol}, type {model_type}, version {version}"
            )
            return None
        try:
            model = joblib.load(model_path)
            self.logger.debug(f"Joblib model loaded from {model_path}")
            return model
        except Exception as e:
            self.logger.error(
                f"Failed to load Joblib model from {model_path}: {e}", exc_info=True
            )
            return None


# -----------------------------------------------------------------------------
# Unified ModelManager (Factory)
# -----------------------------------------------------------------------------
class ModelManager:
    """
    High-level manager that selects the appropriate I/O strategy based on model type.
    Provides unified methods for saving, loading, and validating models.
    """

    # Define supported types for each framework.
    KERAS_TYPES = {"lstm", "neural_network"}
    JOBLIB_TYPES = {
        "random_forest",
        "xgboost",
        "lightgbm",
        "linear_regression",
        "svm",
        "decision_tree",
    }

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.keras_io = KerasModelIO(logger=logger)
        self.joblib_io = JoblibModelIO(logger=logger)
        self.logger.info("ModelManager initialized for Keras and Joblib model types.")

    def save_model(
        self,
        model: Any,
        symbol: str,
        model_type: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        scaler: Optional[Any] = None,
    ) -> Dict[str, Path]:
        """
        Save the model using the appropriate I/O manager based on model_type.
        """
        model_type_lower = model_type.lower()
        if model_type_lower in self.KERAS_TYPES:
            return self.keras_io.save_model(
                model, symbol, model_type, hyperparameters, metrics, scaler
            )
        elif model_type_lower in self.JOBLIB_TYPES:
            return self.joblib_io.save_model(
                model, symbol, model_type, hyperparameters, metrics, scaler
            )
        else:
            self.logger.error(f"Model type '{model_type}' is not supported.")
            raise ValueError(f"Model type '{model_type}' is not supported.")

    def load_model(
        self, symbol: str, model_type: str, version: Optional[str] = None
    ) -> Optional[Any]:
        """
        Load the model by delegating to the appropriate manager.
        """
        model_type_lower = model_type.lower()
        if model_type_lower in self.KERAS_TYPES:
            return self.keras_io.load_model(symbol, model_type, version)
        elif model_type_lower in self.JOBLIB_TYPES:
            return self.joblib_io.load_model(symbol, model_type, version)
        else:
            self.logger.error(f"Model type '{model_type}' is not supported.")
            raise ValueError(f"Model type '{model_type}' is not supported.")

    def validate_model(
        self, symbol: str, model_type: str, version: Optional[str] = None
    ) -> bool:
        """
        Attempt to load the model; return True if loading was successful, else False.
        """
        self.logger.info(
            f"Validating model: symbol={symbol}, type={model_type}, version={version or 'latest'}"
        )
        model = self.load_model(symbol, model_type, version)
        if model:
            self.logger.info(
                f"Model validation successful for {symbol} ({model_type})."
            )
            return True
        self.logger.error(f"Model validation failed for {symbol} ({model_type}).")
        return False

    def load_metadata(
        self, symbol: str, model_type: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Load metadata from the latest or a specific version directory.
        """
        # Choose the appropriate I/O manager
        io_manager = (
            self.keras_io if model_type.lower() in self.KERAS_TYPES else self.joblib_io
        )
        self.logger.info(
            f"Loading metadata for symbol={symbol}, type={model_type}, version={version or 'latest'}"
        )
        metadata_path = io_manager._load_latest_file(
            symbol, model_type, extension="metadata.json", version=version
        )
        if not metadata_path or not metadata_path.exists():
            self.logger.error(
                f"Metadata not found for {symbol}, type {model_type}, version={version}"
            )
            return None
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            self.logger.debug(f"Metadata loaded from {metadata_path}")
            return metadata
        except Exception as e:
            self.logger.error(
                f"Failed to load metadata from {metadata_path}: {e}", exc_info=True
            )
            return None


# -----------------------------------------------------------------------------
# Example Usage (for testing/integration)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    from pathlib import Path

    # Initialize logging using our custom setup_logging.
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logging("model_training_utils", log_dir=log_dir)

    # Initialize Config (using the new config module)
    # (This example assumes your config.py provides the necessary variables.)
    config.validate()  # Validate the configuration

    # Initialize the ModelManager.
    model_manager = ModelManager(logger)

    # Example: Create a dummy Keras LSTM model.
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.models import Sequential

    def create_lstm_model(input_shape: tuple) -> Sequential:
        model = Sequential()
        model.add(LSTM(50, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        model.compile(optimizer="adam", loss="mean_squared_error")
        return model

    symbol = "TSLA"
    model_type = "lstm"
    hyperparameters = {"lstm_units": 50, "dropout_rate": 0.2}
    metrics = {"mse": 0.02, "mae": 0.01}

    lstm_model = create_lstm_model((10, 5))
    saved_files = model_manager.save_model(
        model=lstm_model,
        symbol=symbol,
        model_type=model_type,
        hyperparameters=hyperparameters,
        metrics=metrics,
        scaler=None,
    )
    print("Saved Keras LSTM files:", saved_files)

    # Example: Load the latest LSTM model.
    loaded_lstm_model = model_manager.load_model(symbol, model_type)
    print("Loaded Keras LSTM model:", loaded_lstm_model)

    # Validate model.
    is_valid = model_manager.validate_model(symbol, model_type)
    print(f"Validation status: {is_valid}")

    # Load metadata.
    metadata = model_manager.load_metadata(symbol, model_type)
    if metadata:
        print("Loaded metadata:", json.dumps(metadata, indent=4))
