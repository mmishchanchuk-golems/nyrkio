from pathlib import Path

from backend.mail.sender import render_email

AUTH_TEMPLATES_DIR = Path(__file__).parents[1] / "auth/templates"


def test_render_email_substitutes_and_includes_header_footer():
    html = render_email(AUTH_TEMPLATES_DIR / "verify-email.mjml", verify_url="myurl")
    assert "myurl" in html
    assert "nyrkio.com" in html
