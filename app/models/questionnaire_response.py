from datetime import datetime
from ..extensions import db


class QuestionnaireResponse(db.Model):
    __tablename__ = 'questionnaire_responses'

    id = db.Column(db.Integer, primary_key=True)
    detection_id = db.Column(db.Integer, db.ForeignKey('detections.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_value = db.Column(db.Text, nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
