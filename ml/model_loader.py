import os
import json

try:
    import tensorflow as tf
except Exception:
    tf = None

_BACKEND_ML_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_BACKEND_ML_DIR))
_MODELS_DIR = os.path.join(_PROJECT_ROOT, "models")

SKIN_TYPE_MODEL_PATH = os.path.join(_MODELS_DIR, "skin_type_model.h5")
SKIN_TYPE_LABELS_PATH = os.path.join(_MODELS_DIR, "skin_type_labels.json")
ACNE_MODEL_PATH = os.path.join(_MODELS_DIR, "acne_model.h5")
ACNE_LABELS_PATH = os.path.join(_MODELS_DIR, "acne_labels.json")

_skin_type_model = None
_skin_type_labels = None
_acne_model = None
_acne_labels = None


def _load_h5_model(path):
    """Load a .h5 Keras model, compatible with TF 2.16+ / Keras 3."""
    try:
        return tf.keras.models.load_model(path, compile=False)
    except Exception:
        # Keras 3 fallback: use legacy h5 loader
        import h5py
        with h5py.File(path, 'r') as f:
            return tf.keras.saving.legacy_h5_format.load_model_from_hdf5(f)


def get_skin_type_model():
    global _skin_type_model
    if tf is None:
        raise RuntimeError("TensorFlow is not installed. Run: pip install tensorflow")
    if _skin_type_model is None:
        if not os.path.exists(SKIN_TYPE_MODEL_PATH):
            raise FileNotFoundError(f"Skin type model not found at: {SKIN_TYPE_MODEL_PATH}")
        _skin_type_model = _load_h5_model(SKIN_TYPE_MODEL_PATH)
    return _skin_type_model


def get_skin_type_labels():
    global _skin_type_labels
    if _skin_type_labels is None:
        if not os.path.exists(SKIN_TYPE_LABELS_PATH):
            raise FileNotFoundError(f"Labels file not found at: {SKIN_TYPE_LABELS_PATH}")
        with open(SKIN_TYPE_LABELS_PATH, "r") as f:
            _skin_type_labels = json.load(f)
    return _skin_type_labels


def get_acne_model():
    global _acne_model
    if tf is None:
        raise RuntimeError("TensorFlow is not installed. Run: pip install tensorflow")
    if _acne_model is None:
        if not os.path.exists(ACNE_MODEL_PATH):
            raise FileNotFoundError(f"Acne model not found at: {ACNE_MODEL_PATH}")
        _acne_model = _load_h5_model(ACNE_MODEL_PATH)
    return _acne_model


def get_acne_labels():
    global _acne_labels
    if _acne_labels is None:
        if not os.path.exists(ACNE_LABELS_PATH):
            raise FileNotFoundError(f"Labels file not found at: {ACNE_LABELS_PATH}")
        with open(ACNE_LABELS_PATH, "r") as f:
            _acne_labels = json.load(f)
    return _acne_labels


def reset_cached_models():
    global _skin_type_model, _skin_type_labels, _acne_model, _acne_labels
    _skin_type_model = None
    _skin_type_labels = None
    _acne_model = None
    _acne_labels = None
