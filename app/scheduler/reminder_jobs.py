from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
import logging

_scheduler = BackgroundScheduler()
logger = logging.getLogger(__name__)

# Sri Lanka is UTC+5:30
SL_TZ = timezone(timedelta(hours=5, minutes=30))


def sl_now() -> datetime:
    """Return current naive datetime in Sri Lanka local time."""
    return datetime.now(SL_TZ).replace(tzinfo=None)


def _run_reminders(app):
    with app.app_context():
        try:
            from app.extensions import db
            from app.models.tracking import Tracking
            from app.services.email_service import send_reminder_email

            now_sl = sl_now()
            due = Tracking.query.filter(
                Tracking.is_active == True,
                Tracking.next_reminder <= now_sl,
            ).all()

            for t in due:
                send_reminder_email(t)
                days = 7 if t.frequency == 'weekly' else 30
                t.next_reminder = sl_now() + timedelta(days=days)

            if due:
                db.session.commit()
                logger.info(f"[Reminders] Sent {len(due)} email(s) at {now_sl.strftime('%Y-%m-%d %H:%M')} SL.")
            else:
                logger.debug(f"[Reminders] No due reminders at {now_sl.strftime('%Y-%m-%d %H:%M')} SL.")
        except Exception as e:
            logger.error(f"[Reminders] Job failed: {e}")


def start_scheduler(app):
    if _scheduler.running:
        return
    _scheduler.add_job(
        lambda: _run_reminders(app),
        trigger='interval',
        hours=1,                        # check every hour (not 24)
        id='skinora_reminders',
        replace_existing=True,
        next_run_time=datetime.now(),   # also run once immediately on startup
    )
    _scheduler.start()
    logger.info("APScheduler started — reminders checked every hour (SL timezone).")
