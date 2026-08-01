from flask import current_app
from flask_mail import Message
from ..extensions import mail


def _brand_wrap(content: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;color:#23241C;">
      <div style="background:#6E7733;padding:28px 32px;border-radius:12px 12px 0 0;">
        <h1 style="color:#F6F4EC;font-size:20px;margin:0;">Skinora &#127807;</h1>
      </div>
      <div style="background:#F6F4EC;padding:32px;border-radius:0 0 12px 12px;border:1px solid #E6E3D8;">
        {content}
        <hr style="border:none;border-top:1px solid #E6E3D8;margin:24px 0;">
        <p style="font-size:11px;color:#9C9A8C;line-height:1.5;">
          Skinora &mdash; AI-powered natural skin care. Recommendations are for
          educational purposes only and are not a substitute for professional medical advice.
        </p>
      </div>
    </div>
    """


def send_welcome_email(user) -> bool:
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

    body = f"""
    <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
    <p style="font-size:15px;line-height:1.6;">
      Welcome to <strong>Skinora</strong>! Your account has been created successfully.
      You can now log in and start your personalised skin analysis.
    </p>
    <a href="{frontend_url}/login"
       style="display:inline-block;background:#BECA5C;color:#2A2D14;text-decoration:none;
              padding:14px 28px;border-radius:999px;font-weight:700;font-size:14px;margin:16px 0;">
      Go to Skinora &rarr;
    </a>
    <p style="font-size:13px;color:#6B6A60;margin-top:20px;line-height:1.6;">
      Upload a face photo, get your skin type &amp; acne analysis, and discover
      botanical remedies tailored just for you.
    </p>
    <p style="font-size:12px;color:#9C9A8C;margin-top:16px;">
      If you did not create a Skinora account, you can safely ignore this email.
    </p>
    """
    return _send(
        subject='Welcome to Skinora — your account is ready!',
        recipients=[user.email],
        html=_brand_wrap(body),
    )


def send_reminder_email(tracking) -> None:
    user = tracking.user
    remedy_name = tracking.remedy.name if tracking.remedy else 'your selected remedy'

    body = f"""
    <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
    <p style="font-size:15px;line-height:1.6;">
      It's time for your <strong>{tracking.frequency}</strong> skin check-in.
      How is your skin responding to <strong>{remedy_name}</strong>?
    </p>
    <p style="font-size:14px;color:#6B6A60;margin:20px 0 8px;">Tap your progress below:</p>
    <table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
      <tr>
        <td style="padding:0 8px 0 0;">
          <a href="http://localhost:5173/checkin?status=better&tracking={tracking.id}"
             style="display:inline-block;background:#BECA5C;color:#2A2D14;text-decoration:none;
                    padding:12px 20px;border-radius:999px;font-weight:600;font-size:13px;">
            Getting better &#128077;
          </a>
        </td>
        <td style="padding:0 8px;">
          <a href="http://localhost:5173/checkin?status=no_progress&tracking={tracking.id}"
             style="display:inline-block;background:#F1EEE3;color:#57564E;text-decoration:none;
                    padding:12px 20px;border-radius:999px;font-weight:600;font-size:13px;">
            No change yet
          </a>
        </td>
        <td style="padding:0 0 0 8px;">
          <a href="http://localhost:5173/checkin?status=worse&tracking={tracking.id}"
             style="display:inline-block;background:#FDF4F0;color:#B05E3C;text-decoration:none;
                    padding:12px 20px;border-radius:999px;font-weight:600;font-size:13px;">
            Getting worse
          </a>
        </td>
      </tr>
    </table>
    """
    _send(
        subject=f"Skinora: How is your skin doing with {remedy_name}?",
        recipients=[user.email],
        html=_brand_wrap(body),
    )


def send_adaptive_response_email(user, tracking, status: str, next_remedy_name: str = None) -> None:
    remedy_name = tracking.remedy.name if tracking.remedy else 'your remedy'

    if status == 'better':
        subject = f"Great progress with {remedy_name}! \U0001f33f"
        body = f"""
        <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
        <p style="font-size:15px;line-height:1.6;">
          Your skin is responding well to <strong>{remedy_name}</strong>. Keep it up!
          We'll check in again at your next scheduled date.
        </p>
        """
    elif status == 'no_progress':
        subject = "Let's adjust your remedy — Skinora"
        next_msg = (
            f"<p style='font-size:15px;'>We recommend trying <strong>{next_remedy_name}</strong> next.</p>"
            if next_remedy_name else
            "<p style='font-size:15px;'>Log in to explore other remedies for your condition.</p>"
        )
        body = f"""
        <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
        <p style="font-size:15px;line-height:1.6;">
          Sometimes it takes time to find the right remedy. Let's try a different approach.
        </p>
        {next_msg}
        """
    else:  # worse
        subject = "We recommend seeing a specialist — Skinora"
        body = f"""
        <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
        <p style="font-size:15px;line-height:1.6;">
          We're sorry to hear your skin is getting worse. We strongly recommend consulting
          a qualified dermatologist before continuing any home remedy.
        </p>
        <p style="font-size:15px;line-height:1.6;">
          Your progress tracking has been paused.
        </p>
        """

    _send(subject=subject, recipients=[user.email], html=_brand_wrap(body))


def _send(subject: str, recipients: list, html: str) -> bool:
    try:
        msg = Message(subject=subject, recipients=recipients)
        msg.html = html
        mail.send(msg)
        current_app.logger.info(f"[EMAIL OK] {recipients} — {subject}")
        return True
    except Exception as e:
        import traceback
        current_app.logger.error(
            f"[EMAIL FAILED] {recipients} — {subject}\n"
            f"Error: {e}\n{traceback.format_exc()}"
        )
        return False
