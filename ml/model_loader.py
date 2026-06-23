import os
import json
import tensorflow as tf

# Resolve absolute path to project root → models/
_BACKEND_ML_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_BACKEND_ML_DIR))
_MODELS_DIR = os.path.join(_PROJECT_ROOT, "models")

SKIN_TYPE_MODEL_PATH = os.path.join(_MODELS_DIR, "skin_type_model.h5")
SKIN_TYPE_LABELS_PATH = os.path.join(_MODELS_DIR, "skin_type_labels.json")

_skin_type_model = None
_skin_type_labels = None


def get_skin_type_model() -> tf.keras.Model:
    """
    Load the skin type classification model from disk on first call,
    then cache it in memory for all subsequent calls (singleton).

    Raises FileNotFoundError if skin_type_model.h5 is missing from models/.
    """
    global _skin_type_model
    if _skin_type_model is None:
        if not os.path.exists(SKIN_TYPE_MODEL_PATH):
            raise FileNotFoundError(
                f"Skin type model not found at: {SKIN_TYPE_MODEL_PATH}\n"
                "Train the model using notebooks/train_skin_type.ipynb "
                "and place skin_type_model.h5 in the models/ directory."
            )
        _skin_type_model = tf.keras.models.load_model(SKIN_TYPE_MODEL_PATH)
    return _skin_type_model


def get_skin_type_labels() -> dict:
    """
    Load skin type class label mapping from skin_type_labels.json (singleton).
    Returns a dict mapping string index → class name, e.g. {"0": "dry", ...}.

    Raises FileNotFoundError if the labels file is missing from models/.
    """
    global _skin_type_labels
    if _skin_type_labels is None:
        if not os.path.exists(SKIN_TYPE_LABELS_PATH):
            raise FileNotFoundError(
                f"Labels file not found at: {SKIN_TYPE_LABELS_PATH}\n"
                "Train the model using notebooks/train_skin_type.ipynb "
                "and place skin_type_labels.json in the models/ directory."
            )
        with open(SKIN_TYPE_LABELS_PATH, "r") as f:
            _skin_type_labels = json.load(f)
    return _skin_type_labels


def reset_cached_models() -> None:
    """Force-reload models on the next call. Intended for testing."""
    global _skin_type_model, _skin_type_labels
    _skin_type_model = None
    _skin_type_labels = None
