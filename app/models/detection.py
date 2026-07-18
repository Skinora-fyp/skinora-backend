from datetime import datetime
from ..extensions import db


class Detection(db.Model):
    __tablename__ = 'detections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    skin_type = db.Column(db.Enum('Dry', 'Oily', 'Normal'), nullable=False)
    skin_type_confidence = db.Column(db.Float, nullable=False)
    acne_status = db.Column(db.Enum('Acne', 'NoAcne'), nullable=False)
    acne_confidence = db.Column(db.Float, nullable=False)
    final_condition = db.Column(db.String(50), nullable=False)
    routing = db.Column(db.Enum('direct', 'questionnaire', 'consultant'), nullable=False, default='direct')
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship('QuestionnaireResponse', backref='detection', lazy=True, cascade='all, delete-orphan')
    trackings = db.relationship('Tracking', backref='detection', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'image_url': self.image_url,
            'skin_type': self.skin_type,
            'skin_conf': round(self.skin_type_confidence, 4),
            'acne_status': self.acne_status,
            'acne_conf': round(self.acne_confidence, 4),
            'final_condition': self.final_condition,
            'routing': self.routing,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
        }
