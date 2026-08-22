from datetime import datetime
from ..extensions import db


class EmailOTP(db.Model):
    __tablename__ = 'email_otps'

    id          = db.Column(db.Integer, primary_key=True)
    email       = db.Column(db.String(255), nullable=False, index=True)
    otp_code    = db.Column(db.String(6), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at  = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    @property
    def is_verified(self):
        return self.verified_at is not None
