import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jinja2

from settings import settings


def send_email(
    recipients: list[str],
    /,
    *,
    mail_body: str,
    mail_subject: str,
    attachment: str = None,
):
    TOKEN = settings.SMTP_TOKEN
    USER = settings.SMTP_USER
    SMTP_SERVER = settings.SMTP_SERVER

    msg = MIMEMultipart("alternative")
    msg["Subject"] = mail_subject
    msg["From"] = f"SuperShop {USER}"
    msg["To"] = ", ".join(recipients)
    msg["Reply-To"] = USER
    msg["Return-Path"] = USER
    msg["X-Mailer"] = "decorator"

    text_to_send = MIMEText(mail_body, "html")
    msg.attach(text_to_send)

    if attachment:
        is_file_exists = os.path.exists(attachment)
        if is_file_exists:
            basename = os.path.basename(attachment)
            filesize = os.path.getsize(attachment)
            file = MIMEBase("application", f"octet-stream; name={basename}")
            file.set_payload(open(attachment, "br").read())
            file.add_header("Content-Description", attachment)
            file.add_header(
                "Content-Description",
                f"attachment; filename={attachment}, size={filesize}",
            )
            encoders.encode_base64(file)
            msg.attach(file)

    mail = smtplib.SMTP_SSL(SMTP_SERVER)
    mail.login(USER, TOKEN)
    mail.sendmail(USER, recipients, msg.as_string())
    mail.quit()


def create_body_letter(lang: str, template_name: str, params: dict) -> str:
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template_file = f"templates/{lang}/{template_name}.html"
    template = template_env.get_template(template_file)
    output = template.render(params)
    return output
