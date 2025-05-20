import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    text_content: str = None,
) -> bool:
    """
    Send email using Mailtrap SMTP
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to
    
    # Add text/plain part
    if text_content:
        message.attach(MIMEText(text_content, "plain"))
    
    # Add text/html part
    if html_content:
        message.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP(settings.MAILTRAP_HOST, settings.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(settings.MAILTRAP_USERNAME, settings.MAILTRAP_PASSWORD)
            server.sendmail(
                settings.EMAILS_FROM_EMAIL,
                email_to,
                message.as_string()
            )
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def send_verification_email(email_to: str, verification_token: str) -> bool:
    """
    Send verification email
    """
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
    
    subject = "Coffee Shop - Email Verification"
    
    html_content = f"""
    <html>
        <body>
            <p>Hi there,</p>
            <p>Thank you for signing up with our Coffee Shop!</p>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_link}">Verify Email</a></p>
            <p>If you didn't register for an account, please ignore this email.</p>
            <p>Thanks,<br>Coffee Shop Team</p>
        </body>
    </html>
    """
    
    text_content = f"""
    Hi there,
    
    Thank you for signing up with our Coffee Shop!
    
    Please click the link below to verify your email address:
    {verification_link}
    
    If you didn't register for an account, please ignore this email.
    
    Thanks,
    Coffee Shop Team
    """
    
    return send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
        text_content=text_content
    )