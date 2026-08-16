from datetime import datetime
from ..extensions import db


class CheckinNotification(db.Model):
    __tablename__ = 'checkin_notifications'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tracking_id = db.Column(db.Integer, db.ForeignKey('tracking.id'), nullable=False)
    due_at      = db.Column(db.DateTime, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'id':          self.id,
            'user_id':     self.user_id,
            'tracking_id': self.tracking_id,
            'due_at':      self.due_at.isoformat() if self.due_at else None,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
            'is_resolved': self.is_resolved,
        }
