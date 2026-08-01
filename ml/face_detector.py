"""
OpenCV 4.x Haar cascade face detector.

Requires opencv-python >= 4.x (NOT the 5.0 pre-release — it ships without cascade data files).
Install: pip install opencv-python==4.10.0.84

Uses three frontal-face cascades. Detection parameters are tuned to:
  - ACCEPT: selfies, close-up skin photos, slightly angled faces
  - REJECT: logos, scenery, trees, objects, random non-face images

Key parameters:
  minNeighbors=6   — requires 6 overlapping windows to agree; real faces
                      generate 15-50+ overlapping windows so this passes
                      clear face photos easily, while logos/trees (1-5 windows)
                      are rejected.
  minSize=(80,80)  — face region must be at least 80x80 px in a 1200px image.
  area check       — detected region must cover ≥1% of image area to ignore
                      tiny corner false-positives.
"""
import os
import cv2

_CASCADE_NAMES = [
    'haarcascade_frontalface_default.xml',
    'haarcascade_frontalface_alt2.xml',
    'haarcascade_frontalface_alt.xml',
]

_cascades: list = []

try:
    _data_dir = cv2.data.haarcascades  # e.g. .../cv2/data/
    for _name in _CASCADE_NAMES:
        _path = os.path.join(_data_dir, _name)
        if os.path.isfile(_path):
            _clf = cv2.CascadeClassifier(_path)
            if not _clf.empty():
                _cascades.append(_clf)
    if _cascades:
        print(f'[face_detector] OK — {len(_cascades)} cascade(s) loaded (OpenCV {cv2.__version__})')
    else:
        print('[face_detector] WARNING: cascade files missing — install opencv-python==4.10.0.84')
except Exception as _e:
    print(f'[face_detector] ERROR: {_e}')

# Face region must cover this fraction of image area to count as a real detection.
# Eliminates tiny spurious hits from random textures in corners.
_MIN_FACE_AREA_FRACTION = 0.01


def detect_and_validate_face(image_path: str) -> dict:
    """
    Detect faces in an image using multiple Haar cascades.

    Returns a dict with:
        face_detected (bool)  — True if at least one qualifying face found
        face_count    (int)   — number of qualifying face regions
        face_regions  (list)  — list of {x, y, w, h} dicts
        skipped       (bool)  — True when OpenCV unavailable (cascades not loaded)
    """
    if not _cascades:
        return {"face_detected": True, "face_count": 1, "face_regions": [], "skipped": True}

    img = cv2.imread(image_path)
    if img is None:
        return {"face_detected": False, "face_count": 0, "face_regions": [],
                "error": "Could not read image file"}

    # Resize very large images to a standard size for consistent detection
    h, w = img.shape[:2]
    if max(h, w) > 1200:
        scale = 1200 / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
        h, w = img.shape[:2]

    img_area = h * w
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    raw_faces: list = []
    for clf in _cascades:
        faces = clf.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=6,       # raised from 4 — rejects false positives on logos/scenery
            minSize=(80, 80),     # raised from (30,30) — face must be a meaningful size
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if hasattr(faces, '__len__') and len(faces) > 0:
            raw_faces.extend(faces.tolist())

    # Keep only detections that cover at least 1% of the image area.
    # A 1200×1200 image has area 1,440,000 px; 1% = 14,400 px ≈ 120×120 face.
    qualifying = [
        (x, y, fw, fh) for (x, y, fw, fh) in raw_faces
        if (fw * fh) / img_area >= _MIN_FACE_AREA_FRACTION
    ]

    face_count = len(qualifying)
    face_regions = [
        {"x": int(x), "y": int(y), "w": int(fw), "h": int(fh)}
        for (x, y, fw, fh) in qualifying
    ]

    return {
        "face_detected": face_count > 0,
        "face_count": face_count,
        "face_regions": face_regions,
    }
