import io
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app, send_file
from ..extensions import db
from ..models.tracking import Tracking
from ..models.remedy import Remedy, ConditionRemedy
from ..models.detection import Detection
from ..models.checkin_notification import CheckinNotification
from ..services.email_service import (
    send_adaptive_response_email,
    send_tracking_setup_email,
    send_reminder_email,
    send_progress_report_email,
)
from ..services.pdf_service import generate_progress_pdf
from ..utils import token_required

SL_TZ = timezone(timedelta(hours=5, minutes=30))

def _sl_now():
    """Current naive datetime in Sri Lanka local time (UTC+5:30)."""
    return datetime.now(SL_TZ).replace(tzinfo=None)

tracking_bp = Blueprint('tracking', __name__)


@tracking_bp.route('/create', methods=['POST'])
@token_required
def create_tracking(current_user):
    data = request.get_json() or {}
    frequency = data.get('frequency', 'weekly')
    remedy_id = data.get('remedy_id')
    detection_id = data.get('detection_id')

    if frequency not in ('weekly', 'monthly'):
        return jsonify({'error': 'frequency must be weekly or monthly'}), 400

    if not remedy_id:
        return jsonify({'error': 'remedy_id is required'}), 400

    remedy = db.session.get(Remedy, remedy_id)
    if not remedy:
        return jsonify({'error': 'Remedy not found'}), 404

    if not detection_id:
        latest = (
            Detection.query
            .filter_by(user_id=current_user.id)
            .order_by(Detection.detected_at.desc())
            .first()
        )
        detection_id = latest.id if latest else None

    days = 7 if frequency == 'weekly' else 30
    next_reminder = _sl_now() + timedelta(days=days)

    tracking = Tracking(
        user_id=current_user.id,
        detection_id=detection_id,
        remedy_id=remedy_id,
        frequency=frequency,
        next_reminder=next_reminder,
        is_active=True,
    )
    db.session.add(tracking)
    db.session.commit()

    try:
        send_tracking_setup_email(current_user, tracking)
    except Exception:
        pass  # email failure must never block the API response

    return jsonify({
        'tracking_id': tracking.id,
        'next_reminder': next_reminder.isoformat(),
    }), 201


@tracking_bp.route('', methods=['GET'])
@token_required
def get_tracking(current_user):
    trackings = (
        Tracking.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(Tracking.started_at.desc())
        .all()
    )
    return jsonify({'tracking': [t.to_dict() for t in trackings]}), 200


@tracking_bp.route('/checkin', methods=['POST'])
@token_required
def checkin(current_user):
    data = request.get_json() or {}
    tracking_id = data.get('tracking_id')
    status = data.get('status') or data.get('outcome')

    if status not in ('better', 'no_progress', 'worse'):
        return jsonify({'error': 'status must be better, no_progress, or worse'}), 400

    tracking = Tracking.query.filter_by(
        id=tracking_id, user_id=current_user.id
    ).first() if tracking_id else (
        Tracking.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(Tracking.started_at.desc())
        .first()
    )

    if not tracking:
        return jsonify({'error': 'Tracking record not found'}), 404

    tracking.last_status = status

    next_remedy_name = None
    if status == 'worse':
        tracking.is_active = False
    elif status == 'no_progress' and tracking.detection_id:
        detection = db.session.get(Detection, tracking.detection_id)
        if detection:
            entries = (
                ConditionRemedy.query
                .filter_by(final_condition=detection.final_condition)
                .order_by(ConditionRemedy.sort_order)
                .all()
            )
            remedy_ids = [e.remedy_id for e in entries]
            if tracking.remedy_id in remedy_ids:
                idx = remedy_ids.index(tracking.remedy_id)
                if idx + 1 < len(remedy_ids):
                    nxt = db.session.get(Remedy, remedy_ids[idx + 1])
                    if nxt:
                        next_remedy_name = nxt.name

    db.session.commit()
    send_adaptive_response_email(current_user, tracking, status, next_remedy_name)

    messages = {
        'better': 'Great progress! Keep using your remedy.',
        'no_progress': "Let's try a different approach.",
        'worse': 'We recommend consulting a dermatologist.',
    }
    return jsonify({'status': status, 'message': messages[status]}), 200


@tracking_bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    detections = (
        Detection.query
        .filter_by(user_id=current_user.id)
        .order_by(Detection.detected_at.desc())
        .all()
    )
    trackings = (
        Tracking.query
        .filter_by(user_id=current_user.id)
        .order_by(Tracking.started_at.desc())
        .all()
    )
    return jsonify({
        'user': current_user.to_dict(),
        'detections': [d.to_dict() for d in detections],
        'trackings': [t.to_dict() for t in trackings],
    }), 200


@tracking_bp.route('/due', methods=['GET'])
@token_required
def check_due(current_user):
    """Return whether the user has an active tracking reminder that is due."""
    tracking = (
        Tracking.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(Tracking.started_at.desc())
        .first()
    )
    if not tracking:
        return jsonify({'due': False, 'tracking': None, 'old_detection': None}), 200

    now_sl = _sl_now()
    is_due = bool(tracking.next_reminder and tracking.next_reminder <= now_sl)

    t_dict = tracking.to_dict()
    t_dict['remedy_name'] = tracking.remedy.name if tracking.remedy else None

    old_det = None
    if tracking.detection_id:
        det = db.session.get(Detection, tracking.detection_id)
        old_det = det.to_dict() if det else None

    return jsonify({'due': is_due, 'tracking': t_dict, 'old_detection': old_det}), 200


@tracking_bp.route('/compare', methods=['POST'])
@token_required
def compare_progress(current_user):
    """
    Compare a new detection against the original tracking detection to determine progress.
    Schedules the next reminder automatically after comparison.
    """
    data = request.get_json() or {}
    new_detection_id = data.get('detection_id')

    if not new_detection_id:
        return jsonify({'error': 'detection_id is required'}), 400

    tracking = (
        Tracking.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(Tracking.started_at.desc())
        .first()
    )
    if not tracking:
        return jsonify({'error': 'No active tracking found'}), 404

    new_det = db.session.get(Detection, new_detection_id)
    if not new_det:
        return jsonify({'error': 'New detection not found'}), 404

    old_det = db.session.get(Detection, tracking.detection_id) if tracking.detection_id else None

    def _health_score(det):
        # Acne component (60%): NoAcne+high-confidence is best
        if det.acne_status == 'NoAcne':
            acne_score = float(det.acne_confidence)
        else:
            acne_score = 1.0 - float(det.acne_confidence)

        # Skin type component (40%): Normal=ideal, Dry/Oily=imbalanced
        skin_base = {'Normal': 1.0, 'Dry': 0.55, 'Oily': 0.50}.get(det.skin_type, 0.65)
        conf = float(det.skin_type_confidence)
        # Low-confidence prediction blends toward neutral (0.65)
        skin_score = skin_base * conf + 0.65 * (1.0 - conf)

        return round(acne_score * 0.60 + skin_score * 0.40, 4)

    if old_det:
        old_score = _health_score(old_det)
        new_score = _health_score(new_det)
        delta     = new_score - old_score
        if delta > 0.08:
            progress = 'improved'
        elif delta < -0.08:
            progress = 'worse'
        else:
            progress = 'no_change'
    else:
        old_score = None
        new_score = _health_score(new_det)
        delta     = None
        progress  = 'no_change'

    # Map to Tracking.last_status enum values
    status_map = {'improved': 'better', 'no_change': 'no_progress', 'worse': 'worse'}
    tracking.last_status = status_map[progress]
    days = 7 if tracking.frequency == 'weekly' else 30
    tracking.next_reminder = _sl_now() + timedelta(days=days)

    # Resolve any pending notifications for this user — check-in fulfilled
    now = _sl_now()
    CheckinNotification.query.filter_by(
        user_id=current_user.id, is_resolved=False
    ).update({'is_resolved': True, 'resolved_at': now})

    db.session.commit()

    # Generate PDF report and send via email (non-blocking best-effort)
    try:
        pdf_bytes = generate_progress_pdf(
            user=current_user,
            tracking=tracking,
            old_det=old_det,
            new_det=new_det,
            progress=progress,
            old_score=old_score,
            new_score=new_score,
            delta=delta,
        )
        send_progress_report_email(
            user=current_user,
            progress=progress,
            remedy_name=tracking.remedy.name if tracking.remedy else 'N/A',
            old_score=old_score,
            new_score=new_score,
            delta=delta,
            pdf_bytes=pdf_bytes,
        )
    except Exception as e:
        current_app.logger.error(f'[PDF/EMAIL ERROR] compare_progress: {e}')

    return jsonify({
        'progress':        progress,
        'old_score':       round(old_score, 4) if old_score is not None else None,
        'new_score':       round(new_score, 4),
        'delta':           round(delta, 4) if delta is not None else None,
        'old_image_url':   old_det.image_url if old_det else None,
        'new_image_url':   new_det.image_url,
        'old_condition':   old_det.final_condition if old_det else None,
        'new_condition':   new_det.final_condition,
        'old_acne_status': old_det.acne_status if old_det else None,
        'new_acne_status': new_det.acne_status,
        'frequency':       tracking.frequency,
        'report_emailed':  True,
    }), 200


@tracking_bp.route('/send-reminder', methods=['POST'])
@token_required
def send_reminder_now(current_user):
    """
    Test/manual trigger: immediately sends the reminder email for the
    user's most recent active tracking record. Safe to call at any time.
    """
    tracking = (
        Tracking.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(Tracking.started_at.desc())
        .first()
    )
    if not tracking:
        return jsonify({'error': 'No active tracking found. Set up tracking first.'}), 404

    ok = send_reminder_email(tracking)
    if ok:
        db.session.add(CheckinNotification(
            user_id=current_user.id,
            tracking_id=tracking.id,
            due_at=tracking.next_reminder or _sl_now(),
        ))
        db.session.commit()

    return jsonify({
        'sent': ok,
        'email': current_user.email,
        'remedy': tracking.remedy.name if tracking.remedy else None,
        'frequency': tracking.frequency,
        'next_reminder_sl': tracking.next_reminder.strftime('%Y-%m-%d %H:%M') if tracking.next_reminder else None,
    }), 200 if ok else 500


@tracking_bp.route('/<int:tracking_id>/reminders', methods=['PATCH'])
@token_required
def toggle_reminders(current_user, tracking_id):
    """Pause or resume email reminders for a specific tracking plan."""
    tracking = Tracking.query.filter_by(id=tracking_id, user_id=current_user.id).first()
    if not tracking:
        return jsonify({'error': 'Tracking record not found'}), 404

    data = request.get_json() or {}
    if 'paused' not in data:
        return jsonify({'error': 'paused (bool) is required'}), 400

    tracking.reminders_paused = bool(data['paused'])
    db.session.commit()
    return jsonify({'reminders_paused': tracking.reminders_paused}), 200


@tracking_bp.route('/notifications/count', methods=['GET'])
@token_required
def notifications_count(current_user):
    """Return count of unresolved check-in notifications for the user."""
    count = CheckinNotification.query.filter_by(
        user_id=current_user.id, is_resolved=False
    ).count()
    return jsonify({'count': count}), 200


@tracking_bp.route('/progress-report', methods=['GET'])
@token_required
def download_progress_report(current_user):
    """
    Generate and return a PDF progress report for download.
    Requires ?detection_id=<new_detection_id> query param.
    Compares against the user's active tracking baseline detection.
    """
    detection_id = request.args.get('detection_id', type=int)
    if not detection_id:
        return jsonify({'error': 'detection_id query param required'}), 400

    tracking = (
        Tracking.query
        .filter_by(user_id=current_user.id, is_active=True)
        .order_by(Tracking.started_at.desc())
        .first()
    )
    if not tracking:
        return jsonify({'error': 'No active tracking found'}), 404

    new_det = db.session.get(Detection, detection_id)
    if not new_det or new_det.user_id != current_user.id:
        return jsonify({'error': 'Detection not found'}), 404

    old_det = db.session.get(Detection, tracking.detection_id) if tracking.detection_id else None

    def _score(det):
        if det.acne_status == 'NoAcne':
            acne_score = float(det.acne_confidence)
        else:
            acne_score = 1.0 - float(det.acne_confidence)
        skin_base = {'Normal': 1.0, 'Dry': 0.55, 'Oily': 0.50}.get(det.skin_type, 0.65)
        conf = float(det.skin_type_confidence)
        skin_score = skin_base * conf + 0.65 * (1.0 - conf)
        return round(acne_score * 0.60 + skin_score * 0.40, 4)

    old_score = _score(old_det) if old_det else None
    new_score = _score(new_det)
    delta     = (new_score - old_score) if old_score is not None else None

    if delta is not None:
        progress = 'improved' if delta > 0.08 else ('worse' if delta < -0.08 else 'no_change')
    else:
        progress = 'no_change'

    try:
        pdf_bytes = generate_progress_pdf(
            user=current_user,
            tracking=tracking,
            old_det=old_det,
            new_det=new_det,
            progress=progress,
            old_score=old_score,
            new_score=new_score,
            delta=delta,
        )
    except Exception as e:
        current_app.logger.error(f'[PDF DOWNLOAD ERROR] {e}')
        return jsonify({'error': 'Failed to generate report'}), 500

    buf = io.BytesIO(pdf_bytes)
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='skinora-progress-report.pdf',
    )
