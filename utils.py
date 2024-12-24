# utils.py
import re
import requests
from time import sleep
from requests.exceptions import RequestException
from flask import current_app as app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def send_email(to, subject, body, retry_count = 3, is_html = False):
    sendgrid_key = app.config.get("SENDGRID_API_KEY")
    sendgrid_from = app.config.get("SENDGRID_FROM_ADDRESS")

    if not sendgrid_key or not sendgrid_from:
        app.logger.error("Missing config: SendGrid API configuration is not set!")
        return False
    if not is_valid_email(to):
        app.logger.error(f"Invalid to email address: {to}")
        return False

    for attempt in range(retry_count):
        try:
            sg = SendGridAPIClient(sendgrid_key)
            from_email = Email(sendgrid_from)
            to_email = To(to)
            if is_html:
                content = Content("text/html", body)
            else:
                content = Content("text/plain", body)

            mail = Mail(from_email, to_email, subject, content)
            response = sg.client.mail.send.post(request_body = mail.get())

            if response.status_code == 202:
                app.logger.info(f'Email sent successfully to {to}')
                return True
        except RequestException as e:
            app.logger.error(f"Attempt {attempt + 1}: Error sending email: {e}")
            if attempt < retry_count - 1:
                sleep_time = 2 ** attempt
                app.logger.info(f"Retrying in {sleep_time} seconds...")
                sleep(sleep_time)
        except Exception as e:
            app.logger.error(f"An unexpected error occurred while sending the email: {e}")
            return False
    app.logger.error(f"Max retry attempts exceeded. Email not sent to: {to}")
    return False