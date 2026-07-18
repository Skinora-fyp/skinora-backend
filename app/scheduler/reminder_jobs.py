from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging

_scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)


def _run_reminders(app):
    with app.app_context():
        try:
            from app.extensions import db
            from app.models.tracking import Tracking
            from app.services.email_service import send_reminder_email

            due = Tracking.query.filter(
                Tracking.is_active == True,
                Tracking.next_reminder <= datetime.utcnow(),
            ).all()

            for t in due:
                send_reminder_email(t)
                days = 7 if t.frequency == 'weekly' else 30
                t.next_reminder = datetime.utcnow() + timedelta(days=days)

            if due:
                db.session.commit()
                logger.info(f"Sent {len(due)} reminder email(s).")
        except Exception as e:
            logger.error(f"Reminder job failed: {e}")


def start_scheduler(app):
    if _scheduler.running:
        return
    _scheduler.add_job(
        lambda: _run_reminders(app),
        trigger='interval',
        hours=24,
        id='skinora_reminders',
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("APScheduler started — reminders will run every 24 hours.")
