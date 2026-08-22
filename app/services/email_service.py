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


def send_otp_email(email: str, otp_code: str, name: str = '') -> bool:
    greeting = f"Hi {name}," if name else "Hi there,"
    body = f"""
    <p style="font-size:15px;line-height:1.6;">{greeting}</p>
    <p style="font-size:15px;line-height:1.6;">
      To complete your Skinora account, enter the verification code below.
      It expires in <strong>10 minutes</strong>.
    </p>
    <div style="text-align:center;margin:32px 0;">
      <div style="display:inline-block;background:#23241C;color:#BECA5C;
                  font-family:monospace;font-size:38px;font-weight:800;
                  letter-spacing:14px;padding:22px 36px;border-radius:16px;
                  text-indent:14px;">
        {otp_code}
      </div>
    </div>
    <p style="font-size:13px;color:#6B6A60;line-height:1.6;text-align:center;">
      If you did not request this code, you can safely ignore this email.
    </p>
    """
    return _send(
        subject='Your Skinora verification code',
        recipients=[email],
        html=_brand_wrap(body),
    )


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


def send_tracking_setup_email(user, tracking) -> bool:
    remedy_name = tracking.remedy.name if tracking.remedy else 'your selected remedy'
    frequency   = tracking.frequency
    freq_label  = 'every week' if frequency == 'weekly' else 'every month'
    freq_days   = '7 days'     if frequency == 'weekly' else '30 days'
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

    body = f"""
    <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
    <p style="font-size:15px;line-height:1.6;">
      Your progress tracking is now active for <strong>{remedy_name}</strong>.
      We will send you a check-in reminder <strong>{freq_label}</strong> so you know
      when to upload a new photo and see how your skin is responding.
    </p>
    <div style="background:#F4F6EA;border:1px solid #D5DBA8;border-radius:12px;padding:20px 24px;margin:20px 0;">
      <p style="font-size:13px;color:#5E6A2A;margin:0 0 10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;">Your tracking plan</p>
      <table style="font-size:14px;color:#4F5A2A;border-collapse:collapse;width:100%;">
        <tr><td style="padding:4px 0;color:#9C9A8C;width:130px;">Remedy</td><td><strong>{remedy_name}</strong></td></tr>
        <tr><td style="padding:4px 0;color:#9C9A8C;">Check-in frequency</td><td><strong>{freq_label.capitalize()}</strong></td></tr>
        <tr><td style="padding:4px 0;color:#9C9A8C;">First reminder in</td><td><strong>{freq_days}</strong></td></tr>
      </table>
    </div>
    <p style="font-size:14px;color:#6B6A60;line-height:1.6;">
      When your reminder arrives, take a new photo in the same lighting as your original scan.
      Our AI will compare the images and tell you whether to continue, switch, or seek expert advice.
    </p>
    <a href="{frontend_url}/progress"
       style="display:inline-block;background:#BECA5C;color:#2A2D14;text-decoration:none;
              padding:14px 28px;border-radius:999px;font-weight:700;font-size:14px;margin:16px 0;">
      View my progress dashboard &rarr;
    </a>
    """
    return _send(
        subject=f"Tracking started ✓ — reminder {freq_label} for {remedy_name}",
        recipients=[user.email],
        html=_brand_wrap(body),
    )


def send_reminder_email(tracking) -> bool:
    user        = tracking.user
    remedy_name = tracking.remedy.name if tracking.remedy else 'your selected remedy'
    frequency   = tracking.frequency
    freq_label  = 'weekly' if frequency == 'weekly' else 'monthly'
    freq_days   = '7 days' if frequency == 'weekly' else '30 days'
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')

    body = f"""
    <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
    <p style="font-size:15px;line-height:1.6;">
      Your <strong>{freq_label} skin check-in</strong> is ready.
      It has been <strong>{freq_days}</strong> since you started using
      <strong>{remedy_name}</strong> — time to take a new photo and see how your skin is responding.
    </p>
    <div style="background:#F4F6EA;border:1px solid #D5DBA8;border-radius:12px;padding:18px 22px;margin:20px 0;">
      <p style="font-size:13px;color:#5E6A2A;margin:0 0 8px;font-weight:600;
                text-transform:uppercase;letter-spacing:.06em;">How it works</p>
      <ol style="font-size:14px;color:#4F5A2A;line-height:1.8;margin:0;padding-left:18px;">
        <li>Log in to your Skinora account</li>
        <li>Upload a new photo — same lighting as your first scan</li>
        <li>Our AI compares the images and tells you: Improved, No change, or Worse</li>
      </ol>
    </div>
    <p style="font-size:14px;color:#6B6A60;line-height:1.6;margin:0 0 20px;">
      The whole process takes about 30 seconds.
      Your progress dashboard will update automatically after the scan.
    </p>
    <a href="{frontend_url}/progress"
       style="display:inline-block;background:#BECA5C;color:#2A2D14;text-decoration:none;
              padding:14px 32px;border-radius:999px;font-weight:700;font-size:15px;margin-bottom:8px;">
      Log in &amp; check my progress &rarr;
    </a>
    <p style="font-size:12px;color:#A8A698;margin-top:20px;line-height:1.6;">
      You are receiving this because you set up {freq_label} progress tracking on Skinora.
    </p>
    """
    return _send(
        subject=f"Your {freq_label} skin check-in is ready — Skinora 🌿",
        recipients=[user.email],
        html=_brand_wrap(body),
    )


def send_progress_report_email(user, progress: str, remedy_name: str,
                               old_score, new_score, delta,
                               pdf_bytes: bytes) -> bool:
    """Send the post-check-in email with the PDF progress report attached."""
    vcfg = {
        'improved':  ('#3E7A2A', 'Your skin is improving', '🌿 Great progress!',
                      'Keep using your remedy and check back at your next scheduled date.'),
        'no_change': ('#8A6B1E', 'No significant change yet', '→ Steady as she goes',
                      'Some remedies take 4–8 weeks. Log in to explore alternatives if you prefer.'),
        'worse':     ('#B05E3C', 'Your skin needs attention', '⚠ Please review your remedy',
                      'Consider pausing the remedy and consulting a dermatologist.'),
    }
    accent, subject_suffix, headline, guidance = vcfg.get(
        progress, ('#9C9A8C', 'Check-in complete', 'Check-in done', ''))

    sign  = '+' if (delta or 0) >= 0 else ''
    delta_str = f'{sign}{(delta or 0) * 100:.1f}%' if delta is not None else 'N/A'

    body = f"""
    <p style="font-size:15px;line-height:1.6;">Hi {user.name},</p>
    <p style="font-size:15px;line-height:1.6;">
      Your Skinora skin check-in is complete. Here is a summary of your results.
      Your full progress report is attached as a PDF.
    </p>

    <!-- Verdict card -->
    <div style="border-left:4px solid {accent};background:#F8F7F2;
                border-radius:0 12px 12px 0;padding:18px 22px;margin:20px 0;">
      <div style="font-size:18px;font-weight:700;color:{accent};margin-bottom:6px;">{headline}</div>
      <div style="font-size:13px;color:#6B6A60;line-height:1.6;">{guidance}</div>
    </div>

    <!-- Score table -->
    <table style="width:100%;border-collapse:collapse;font-size:14px;margin:16px 0;">
      <tr style="background:#F4F6EA;">
        <td style="padding:10px 14px;color:#5E6A2A;font-weight:600;">Remedy</td>
        <td style="padding:10px 14px;color:#23241C;">{remedy_name}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;color:#9C9A8C;">Original health score</td>
        <td style="padding:10px 14px;color:#23241C;">{f"{old_score*100:.1f}%" if old_score is not None else "N/A"}</td>
      </tr>
      <tr style="background:#F4F6EA;">
        <td style="padding:10px 14px;color:#9C9A8C;">Check-in health score</td>
        <td style="padding:10px 14px;color:#23241C;">{new_score*100:.1f}%</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;color:#9C9A8C;">Net change</td>
        <td style="padding:10px 14px;font-weight:700;color:{accent};">{delta_str}</td>
      </tr>
    </table>

    <p style="font-size:13px;color:#6B6A60;line-height:1.6;">
      Your detailed progress report (with scan images and recommendations) is attached to this email as a PDF.
      You can also log in to your Skinora dashboard to view and download it at any time.
    </p>
    """

    try:
        from flask_mail import Message
        from ..extensions import mail
        from flask import current_app

        msg = Message(
            subject=f'Skinora check-in complete — {subject_suffix}',
            recipients=[user.email],
        )
        msg.html = _brand_wrap(body)
        msg.attach(
            filename='skinora-progress-report.pdf',
            content_type='application/pdf',
            data=pdf_bytes,
        )
        mail.send(msg)
        current_app.logger.info(f'[EMAIL+PDF OK] {user.email} — progress report')
        return True
    except Exception as e:
        import traceback
        from flask import current_app
        current_app.logger.error(
            f'[EMAIL+PDF FAILED] {user.email}\nError: {e}\n{traceback.format_exc()}'
        )
        return False


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
