import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from string import Template

import httpx
from mjml import mjml2html

POSTMARK_API_KEY = os.environ.get("POSTMARK_API_KEY", None)

# When set, emails are sent via plain SMTP (e.g. to a local Mailhog
# instance) instead of the Postmark HTTP API. Intended for local dev only.
SMTP_HOST = os.environ.get("SMTP_HOST", None)
SMTP_PORT = int(os.environ.get("SMTP_PORT", 1025))

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_email(body_template_path: Path, **kwargs) -> str:
    """
    Render a per-feature body fragment inside the shared mail/templates/base.mjml
    layout (header + footer). All template images (logo, background, social
    icons) are hosted on the ImageKit CDN directly from base.mjml - see there.
    """
    body = Template(body_template_path.read_text()).substitute(**kwargs)
    shell = Template((TEMPLATES_DIR / "base.mjml").read_text()).substitute(body=body)
    return mjml2html(shell, include_loader=lambda p: (TEMPLATES_DIR / p).read_text())


async def send_email(email: str, subject: str, html: str):
    if SMTP_HOST:
        _send_email_smtp(email, subject, html)
        return

    with httpx.Client() as client:
        url = "https://api.postmarkapp.com/email"
        response = client.post(
            url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": POSTMARK_API_KEY,
            },
            json={
                "From": "helloworld@nyrkio.com",
                "To": email,
                "Subject": subject,
                "HtmlBody": html,
                "MessageStream": "outbound",
            },
        )
        if response.status_code != 200:
            logging.error(f"Failed to send email: {response.status_code}")


def _send_email_smtp(email: str, subject: str, html: str):
    """
    Send an email over plain SMTP, e.g. to a local Mailhog instance.
    """
    message = MIMEMultipart("related")
    message["Subject"] = subject
    message["From"] = "helloworld@nyrkio.com"
    message["To"] = email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(message["From"], [email], message.as_string())
    except OSError as e:
        logging.error(f"Failed to send email via SMTP {SMTP_HOST}:{SMTP_PORT}: {e}")
