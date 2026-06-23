import numpy as np
from PIL import Image

IMG_SIZE = (224, 224)


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Load an image from disk, resize to 224×224, and return raw float32 pixels
    in [0, 255]. EfficientNetV2S is saved with include_preprocessing=True so it
    applies its own internal normalization — do not apply any external scaling.
    Returns a (1, 224, 224, 3) float32 array ready for model.predict().
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    return np.expand_dims(img_array, axis=0)


def preprocess_pil_image(pil_image: Image.Image) -> np.ndarray:
    """
    Preprocess a PIL Image object for EfficientNetV2S inference.
    Accepts any PIL Image (will be converted to RGB), returns (1, 224, 224, 3)
    float32 array with raw [0, 255] pixel values.
    """
    img = pil_image.convert("RGB").resize(IMG_SIZE, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    return np.expand_dims(img_array, axis=0)
