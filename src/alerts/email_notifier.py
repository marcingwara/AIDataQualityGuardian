import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.logger import logger


class EmailNotifier:
    """
    Sends Data Quality reports via email using SMTP.

    Supports:
    - Gmail SMTP
    - Outlook / Office365 SMTP
    - Enterprise SMTP servers

    Usage:
        emailer = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="your-email@gmail.com",
            password="your-app-password",
            from_email="your-email@gmail.com",
            to_emails=["recipient@company.com"]
        )

        emailer.send_report("subject", "message text or HTML")
    """

    def __init__(self, smtp_host, smtp_port, username, password, from_email, to_emails):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails if isinstance(to_emails, list) else [to_emails]

    # -------------------------------------
    # Send plain text or HTML report
    # -------------------------------------
    def send_report(self, subject: str, message: str, is_html: bool = False):
        """
        Sends an email with the given subject and body.
        If is_html=True → sends formatted HTML email.
        """

        try:
            logger.info("Preparing email message...")

            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = subject

            if is_html:
                msg.attach(MIMEText(message, "html"))
            else:
                msg.attach(MIMEText(message, "plain"))

            logger.info("Connecting to SMTP server...")

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, self.to_emails, msg.as_string())

            logger.info("Email sent successfully.")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False