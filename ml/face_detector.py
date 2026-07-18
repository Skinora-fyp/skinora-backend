import os
import sys
import glob

_CASCADE_NAMES = [
    "haarcascade_frontalface_default.xml",
    "haarcascade_frontalface_alt2.xml",
    "haarcascade_frontalface_alt.xml",
    "haarcascade_profileface.xml",
]


def _find_cascade(filename: str) -> str | None:
    candidates = []
    try:
        import cv2
        own_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(own_dir, filename))

        if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
            candidates.append(cv2.data.haarcascades + filename)

        cv2_dir = os.path.dirname(cv2.__file__)
        candidates.append(os.path.join(cv2_dir, 'data', filename))
        candidates.append(os.path.join(sys.prefix, 'Library', 'etc', 'haarcascades', filename))
        candidates.append(os.path.join(sys.prefix, 'share', 'opencv4', 'haarcascades', filename))
        candidates.append(os.path.join(sys.prefix, 'share', 'OpenCV', 'haarcascades', filename))

        for found in glob.glob(os.path.join(sys.prefix, '**', filename), recursive=True):
            candidates.append(found)
    except Exception:
        pass

    for p in candidates:
        if p and os.path.isfile(p):
            return p
    return None


try:
    import cv2

    _cascades = []
    for _name in _CASCADE_NAMES:
        _path = _find_cascade(_name)
        if _path:
            _clf = cv2.CascadeClassifier(_path)
            if not _clf.empty():
                _cascades.append((_name, _clf))

    _CV2_OK = len(_cascades) > 0
    if _CV2_OK:
        print(f"[face_detector] OK — {len(_cascades)} cascade(s) loaded: {[n for n,_ in _cascades]}")
    else:
        print("[face_detector] WARNING: No cascade classifiers loaded — face validation disabled.")

except Exception as _e:
    _CV2_OK = False
    _cascades = []
    print(f"[face_detector] WARNING: OpenCV unavailable ({_e}) — face validation disabled.")


def detect_and_validate_face(image_path: str) -> dict:
    """
    Detect faces using multiple OpenCV Haar cascades with relaxed parameters.
    Tries frontal (default + alt + alt2) and profile cascades.
    Returns face_detected=True if any cascade finds at least one face.
    """
    if not _CV2_OK:
        return {"face_detected": True, "face_count": 1, "face_regions": [], "skipped": True}

    img = cv2.imread(image_path)
    if img is None:
        return {"face_detected": False, "face_count": 0, "face_regions": [],
                "error": "Could not read image file"}

    # Resize very large images to speed up detection
    h, w = img.shape[:2]
    if max(h, w) > 1200:
        scale = 1200 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Equalise histogram to handle varied lighting
    gray = cv2.equalizeHist(gray)

    all_faces = []
    for _, clf in _cascades:
        # Relaxed parameters: lower minNeighbors and minSize catch angled / partial faces
        faces = clf.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=3,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if hasattr(faces, '__len__') and len(faces) > 0:
            all_faces.extend(faces.tolist())

    face_count = len(all_faces)
    face_regions = [
        {"x": int(x), "y": int(y), "w": int(w2), "h": int(h2)}
        for (x, y, w2, h2) in all_faces
    ]

    return {
        "face_detected": face_count > 0,
        "face_count": face_count,
        "face_regions": face_regions,
    }
