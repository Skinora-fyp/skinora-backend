import sys
import os

_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from ml.predictor import predict_skin_type, predict_acne
from .fusion_layer import fuse


def run_dual_prediction(image_path: str) -> dict:
    """
    Run both ML models on the image and return combined results.
    Raises ValueError if no face detected in the image.

    Returns:
        {
            skin_type: str,        # 'Dry' | 'Oily' | 'Normal'
            skin_conf: float,      # 0.0 – 1.0
            acne_status: str,      # 'Acne' | 'NoAcne'
            acne_conf: float,      # 0.0 – 1.0
            final_condition: str,  # e.g. 'Oily_Acne'
        }
    """
    skin_result = predict_skin_type(image_path)
    acne_result = predict_acne(image_path)

    raw_skin = skin_result['skin_type']
    skin_type = raw_skin.capitalize() if raw_skin.islower() else raw_skin

    raw_acne = acne_result['acne_class']
    acne_status = 'Acne' if acne_result['has_acne'] else 'NoAcne'

    skin_conf = round(skin_result['confidence'] / 100.0, 4)
    acne_conf = round(acne_result['confidence'] / 100.0, 4)

    final_condition = fuse(skin_type, acne_status)

    return {
        'skin_type': skin_type,
        'skin_conf': skin_conf,
        'acne_status': acne_status,
        'acne_conf': acne_conf,
        'final_condition': final_condition,
    }
