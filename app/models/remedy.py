from ..extensions import db


class Remedy(db.Model):
    __tablename__ = 'remedies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ingredients = db.Column(db.JSON, nullable=True)
    instructions = db.Column(db.JSON, nullable=False)
    confidence_level = db.Column(db.Enum('High', 'Medium'), default='High')
    source_url = db.Column(db.Text, nullable=True)
    lifestyle_tags = db.Column(db.JSON, nullable=True)

    condition_entries = db.relationship('ConditionRemedy', backref='remedy', lazy=True)
    trackings = db.relationship('Tracking', backref='remedy', lazy=True)

    def to_dict(self):
        _TINTS = ['#C6D29A', '#D4C5A9', '#B8C9A3', '#C9B99A', '#A8BEA0', '#D6C8A0', '#B5CCA8']
        _TAG_LABELS = {
            'high_stress': 'Stress-related skin', 'low_water': 'Low hydration',
            'poor_sleep': 'Poor sleep', 'dairy': 'Dairy-sensitive', 'oily': 'Oily skin',
        }
        tags = self.lifestyle_tags or []
        instructions = self.instructions or []
        tint = _TINTS[(self.id - 1) % len(_TINTS)] if self.id else _TINTS[0]
        for_label = ' · '.join(_TAG_LABELS.get(t, t) for t in tags[:2]) or 'All skin types'
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients or [],
            'instructions': instructions,
            'confidence_level': self.confidence_level,
            'source_url': self.source_url,
            'lifestyle_tags': tags,
            # Visual fields the frontend card/detail pages require
            'tag': 'High evidence' if self.confidence_level == 'High' else 'Medium evidence',
            'match': 95 if self.confidence_level == 'High' else 80,
            'tint': tint,
            'image': None,
            'desc': instructions[0] if instructions else self.name,
            'source': self.source_url or '',
            'sourceUrl': self.source_url or '',
            'steps': instructions,
            'for': for_label,
            'freq': 'Daily application',
        }


class ConditionRemedy(db.Model):
    __tablename__ = 'condition_remedies'

    id = db.Column(db.Integer, primary_key=True)
    final_condition = db.Column(db.String(50), nullable=False)
    remedy_id = db.Column(db.Integer, db.ForeignKey('remedies.id'), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('final_condition', 'remedy_id', name='uq_condition_remedy'),
    )
