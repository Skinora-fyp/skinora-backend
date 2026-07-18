from ..extensions import db


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    relevance = db.Column(db.JSON, nullable=True)
    answer_type = db.Column(db.Enum('yes_no', 'scale_1_5', 'multiple_choice'), nullable=False)
    answer_options = db.Column(db.JSON, nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'category': self.category,
            'answer_type': self.answer_type,
            'answer_options': self.answer_options,
            'sort_order': self.sort_order,
        }
