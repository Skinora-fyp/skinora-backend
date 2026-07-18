import os
import tempfile
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify, current_app
from ..extensions import db
from ..models.detection import Detection
from ..services.ai_service import run_dual_prediction
from ..services.confidence_router import get_routing
from ..utils import token_required

detection_bp = Blueprint('detection', __name__)

ALLOWED_MIME = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}


@detection_bp.route('/detect', methods=['POST'])
@token_required
def detect(current_user):
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided. Use multipart field name "image".'}), 400

    file = request.files['image']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400
    if file.content_type not in ALLOWED_MIME:
        return jsonify({'error': 'Only JPEG, PNG and WebP images are accepted'}), 400

    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else '.jpg'
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    image_url = ''
    try:
        result = run_dual_prediction(tmp_path)

        # Upload to Cloudinary
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET'],
        )
        upload = cloudinary.uploader.upload(
            tmp_path,
            folder=current_app.config.get('CLOUDINARY_FOLDER', 'skinora/uploads'),
            resource_type='image',
            quality='auto',
            fetch_format='auto',
        )
        image_url = upload.get('secure_url', '')

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        current_app.logger.error(f"Detection error:\n{tb}")
        return jsonify({'error': str(e), 'detail': tb}), 500
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    routing = get_routing(result['skin_conf'], result['acne_conf'])

    detection = Detection(
        user_id=current_user.id,
        image_url=image_url,
        skin_type=result['skin_type'],
        skin_type_confidence=result['skin_conf'],
        acne_status=result['acne_status'],
        acne_confidence=result['acne_conf'],
        final_condition=result['final_condition'],
        routing=routing,
    )
    db.session.add(detection)
    db.session.commit()

    return jsonify({
        'detection_id': detection.id,
        'skin_type': result['skin_type'],
        'skin_conf': result['skin_conf'],
        'acne_status': result['acne_status'],
        'acne_conf': result['acne_conf'],
        'final_condition': result['final_condition'],
        'routing': routing,
        'image_url': image_url,
    }), 200


@detection_bp.route('/detections', methods=['GET'])
@token_required
def list_detections(current_user):
    detections = (
        Detection.query
        .filter_by(user_id=current_user.id)
        .order_by(Detection.detected_at.desc())
        .limit(20)
        .all()
    )
    return jsonify({'detections': [d.to_dict() for d in detections]}), 200
