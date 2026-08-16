from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.tracking import Tracking
from ..models.remedy import Remedy, ConditionRemedy
from ..models.detection import Detection
from ..services.email_service import (
    send_adaptive_response_email,
    send_tracking_setup_email,
    send_reminder_email,
)
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
    return jsonify({
        'sent': ok,
        'email': current_user.email,
        'remedy': tracking.remedy.name if tracking.remedy else None,
        'frequency': tracking.frequency,
        'next_reminder_sl': tracking.next_reminder.strftime('%Y-%m-%d %H:%M') if tracking.next_reminder else None,
    }), 200 if ok else 500
