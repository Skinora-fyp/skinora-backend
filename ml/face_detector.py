import cv2

HAAR_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
_face_cascade = None


def _get_cascade() -> cv2.CascadeClassifier:
    global _face_cascade
    if _face_cascade is None:
        _face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    return _face_cascade


def detect_and_validate_face(image_path: str) -> dict:
    """
    Run OpenCV Haar cascade face detection on the given image file.

    Returns:
        {
            "face_detected": bool,
            "face_count": int,
            "face_regions": list[dict]   # each: {x, y, w, h}
        }
    On read failure, face_detected is False and an "error" key is included.
    """
    img = cv2.imread(image_path)
    if img is None:
        return {
            "face_detected": False,
            "face_count": 0,
            "face_regions": [],
            "error": f"Could not read image at path: {image_path}",
        }

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = _get_cascade()

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80),
    )

    face_count = len(faces)
    face_regions = (
        [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for (x, y, w, h) in faces]
        if face_count > 0
        else []
    )

    return {
        "face_detected": face_count > 0,
        "face_count": face_count,
        "face_regions": face_regions,
    }
