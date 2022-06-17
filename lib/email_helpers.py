import project_settings
import asyncio
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lib.logger import CustomLogger
from lib.messages import MAILS_MAPPING
from email.mime.base import MIMEBase
from email import encoders
logger = CustomLogger.get_logger('flask')


async def send_mail(message_data: dict, attach=None):
    try:
        message = MIMEMultipart('alternative')
        message['From'] = project_settings.MAIL_FROM
        message['To'] = message_data['recipients'][0]
        message['Subject'] = message_data['subject']
        plain_text_message = MIMEText(message_data['body'], 'plain', 'utf-8')
        html_message = MIMEText(message_data['html'], 'html', 'utf-8')
        message.attach(plain_text_message)
        message.attach(html_message)
        if attach:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open("current_statuses.xls", "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="current_statuses.xls"')
            message.attach(part)

        asyncio.create_task(aiosmtplib.send(
            message,
            recipients=message_data['recipients'],
            hostname=project_settings.MAIL_SERVER,
            port=587,
            username=project_settings.MAIL_FROM,
            password=project_settings.MAIL_PASSWORD,
            start_tls=True,
            timeout=10,
        ))

    except Exception:
        logger.exception('Mail message sent to %s has been failed', message_data['recipients'])
        raise

    logger.info('Email message has been sent to %s ', message_data['recipients'])


def build_email_message(
        recipients: list,
        message=None,
        message_type=None
) -> dict:
    mail_data = MAILS_MAPPING[message_type]

    return dict(
        email_from=project_settings.MAIL_FROM,
        recipients=recipients,
        subject=mail_data['subject'],
        body=mail_data['text'].format(message),
        html=mail_data['text'].format(message),
    )


