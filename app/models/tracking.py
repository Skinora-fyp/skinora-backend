from datetime import datetime
from ..extensions import db


class Tracking(db.Model):
    __tablename__ = 'tracking'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    detection_id = db.Column(db.Integer, db.ForeignKey('detections.id'), nullable=True)
    remedy_id = db.Column(db.Integer, db.ForeignKey('remedies.id'), nullable=False)
    frequency = db.Column(db.Enum('weekly', 'monthly'), nullable=False, default='weekly')
    next_reminder = db.Column(db.DateTime, nullable=True)
    last_status = db.Column(db.Enum('better', 'no_progress', 'worse'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'detection_id': self.detection_id,
            'remedy_id': self.remedy_id,
            'remedy_name': self.remedy.name if self.remedy else None,
            'frequency': self.frequency,
            'next_reminder': self.next_reminder.isoformat() if self.next_reminder else None,
            'last_status': self.last_status,
            'is_active': self.is_active,
            'started_at': self.started_at.isoformat() if self.started_at else None,
        }
