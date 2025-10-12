import asyncio
import smtplib
from email.message import EmailMessage

from jinja2 import Environment, FileSystemLoader
from app.config import email_config

env = Environment(loader=FileSystemLoader("app/modules/email/templates"))

def send_email(to, subject, html):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_config.STMP_EMAIL_ADDRESS
    msg["To"] = to
    msg.set_content("Для просмотра письма включите HTML.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL(email_config.SMTP_SERVER, email_config.SMTP_PORT) as smtp:
        smtp.login(email_config.STMP_EMAIL_ADDRESS, email_config.STMP_PASSWORD)
        smtp.send_message(msg)

async def send_notification_email(to: str, book_title: str) -> bool:
    try:
        template = env.get_template("email_notification.html")
        html = template.render(book_title=book_title)
        subject = "Книга в наличии"

        await asyncio.to_thread(send_email,to,subject, html)

        return True
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
        return False

async def send_verify_email(to: str, token: str) -> bool:
    try:
        verify_url = f"http://localhost/api/users/verify?token={token}"
        template = env.get_template("verify_email.html")
        html = template.render(verify_url=verify_url)
        subject = "Подтвердите почту"

        await asyncio.to_thread(send_email, to, subject, html)

        return True
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
        return False
