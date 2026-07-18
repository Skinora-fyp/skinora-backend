import numpy as np

from .face_detector import detect_and_validate_face
from .model_loader import (
    get_skin_type_model, get_skin_type_labels,
    get_acne_model, get_acne_labels,
)
from .preprocessing import preprocess_image


def predict_skin_type(image_path: str) -> dict:
    """
    Run the full skin type detection pipeline on a single image file.

    Pipeline:
        1. Face validation  (OpenCV Haar cascade)
        2. Preprocessing    (resize 224×224, raw float32 for EfficientNetV2S)
        3. Model inference  (EfficientNetV2S classifier)
        4. Result formatting

    Args:
        image_path: Absolute or relative path to the uploaded image file.

    Returns:
        {
            "skin_type":     str,   # "dry" | "normal" | "oily"
            "confidence":    float, # dominant class confidence as percentage
            "probabilities": dict,  # {"dry": 12.45, "normal": 0.21, "oily": 87.34}
            "face_detected": bool,
            "face_count":    int
        }

    Raises:
        ValueError: No face detected — caller should return HTTP 400.
        FileNotFoundError: Model files missing from models/ — server config error.
    """
    face_result = detect_and_validate_face(image_path)
    if not face_result["face_detected"]:
        raise ValueError(
            "No face detected in the uploaded image. "
            "Please upload a clear, well-lit frontal facial photograph."
        )

    model = get_skin_type_model()
    labels = get_skin_type_labels()

    img_array = preprocess_image(image_path)
    raw_predictions = model.predict(img_array, verbose=0)
    probabilities = raw_predictions[0]

    predicted_index = int(np.argmax(probabilities))
    predicted_class = labels[str(predicted_index)]
    confidence = float(probabilities[predicted_index]) * 100

    all_probabilities = {
        labels[str(i)]: round(float(prob) * 100, 2)
        for i, prob in enumerate(probabilities)
    }

    return {
        "skin_type": predicted_class,
        "confidence": round(confidence, 2),
        "probabilities": all_probabilities,
        "face_detected": True,
        "face_count": face_result["face_count"],
    }


def predict_acne(image_path: str) -> dict:
    """
    Run the full acne detection pipeline on a single image file.

    Pipeline:
        1. Face validation  (OpenCV Haar cascade)
        2. Preprocessing    (resize 224×224, raw float32 for EfficientNetV2S)
        3. Model inference  (EfficientNetV2S binary classifier)
        4. Result formatting

    Args:
        image_path: Absolute or relative path to the uploaded image file.

    Returns:
        {
            "has_acne":      bool,  # True when predicted class is "acne"
            "acne_class":    str,   # "acne" | "no_acne"
            "confidence":    float, # dominant class confidence as percentage
            "probabilities": dict,  # {"acne": 87.34, "no_acne": 12.66}
            "face_detected": bool,
            "face_count":    int
        }

    Raises:
        ValueError: No face detected — caller should return HTTP 400.
        FileNotFoundError: Model files missing from models/ — server config error.
    """
    face_result = detect_and_validate_face(image_path)
    if not face_result["face_detected"]:
        raise ValueError(
            "No face detected in the uploaded image. "
            "Please upload a clear, well-lit frontal facial photograph."
        )

    model = get_acne_model()
    labels = get_acne_labels()

    img_array = preprocess_image(image_path)
    raw_predictions = model.predict(img_array, verbose=0)
    probabilities = raw_predictions[0]

    predicted_index = int(np.argmax(probabilities))
    predicted_class = labels[str(predicted_index)]
    confidence = float(probabilities[predicted_index]) * 100

    all_probabilities = {
        labels[str(i)]: round(float(prob) * 100, 2)
        for i, prob in enumerate(probabilities)
    }

    return {
        "has_acne": predicted_class == "acne",
        "acne_class": predicted_class,
        "confidence": round(confidence, 2),
        "probabilities": all_probabilities,
        "face_detected": True,
        "face_count": face_result["face_count"],
    }
