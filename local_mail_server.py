import os
import smtplib
import threading
from email.mime.text import MIMEText

import localmail
from dotenv import load_dotenv

load_dotenv()

SMTP_PORT = int(os.getenv('SMTP_PORT'))
IMAP_PORT = int(os.getenv('IMAP_PORT'))
HTTP_PORT = int(os.getenv('HTTP_PORT'))
Mailbox_File = os.getenv('Mailbox_File')


class LocalMailServer:
    def __init__(self):
        self.thread = threading.Thread(
            target=localmail.run,
            args=(SMTP_PORT, IMAP_PORT, HTTP_PORT, Mailbox_File)
        )

    def start(self):
        self.thread.start()
        print(f"localmail server started on SMTP port {SMTP_PORT}, IMAP port {IMAP_PORT}, HTTP port {HTTP_PORT}")
        print(f"Received emails will be saved to {Mailbox_File}")

    def send_email(self, email):
        print("sending email")
        msg = MIMEText(email['Content'])
        msg['Subject'] = email['Subject']
        msg['From'] = email['From']
        msg['To'] = email['To']
        try:
            with smtplib.SMTP('localhost', int(SMTP_PORT)) as server:
                server.send_message(msg)
            print("Email sent successfully to localmail.")
        except Exception as e:
            print(f"Error sending email: {e}")

    def stop_server(self):
        localmail.shutdown_thread(self.thread)
        print("localmail server shut down.")
