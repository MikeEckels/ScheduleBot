import os
import dotenv
import smtplib
import logging
from Email import Email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class EmailClient():
    def __init__(self):
        self.__reset()

    def __reset(self):
        dotenv.load_dotenv()
        self.__email = Email()
        self.__SMTPPort = 587
        self.__SMTPServer = "smtp.gmail.com"
        self.__password = os.environ.get("EMAIL_PASSWORD")
        self.__senderEmail = os.environ.get("SENDER_EMAIL")
        self.__message = MIMEMultipart('mixed')
        self.__alternative = MIMEMultipart('alternative')
        self.__Bcc = ""

        self.__logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                            level = logging.INFO,
                            datefmt = '%m/%d %H:%M'
        )
    
    def __attachDoc(self, attachmentPath):
        if attachmentPath and os.path.exists(attachmentPath):
            with open(attachmentPath, "rb") as document:
                doc = MIMEApplication(document.read(), Name = os.path.basename(attachmentPath))
            doc['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachmentPath)}"'
            self.__message.attach(doc)

    def createEmail(self, to, date, logo, searchResults, attachmentPath = None):
        self.__reset()
        name, to, *self.__Bcc = to
        self.__message['To'] = to
        self.__message['From'] = self.__senderEmail

        lastName = name.split(',')[0].title()
        matches = searchResults.get(name, {}).get("matches", [])

        self.__message['Subject'] = self.__email.subject.format(
            schedDate = date,
            lastName = lastName
        )

        textResults = "\n".join(f"Page {p}: {l}" for p, l in matches)
        htmlResults = "".join(f"<li style='margin-bottom:8px;'>Page {p}: {l}</li>" for p, l in matches)

        bodyText = self.__email.bodyText.format(
            lastName = lastName,
            schedDate = date,
            textResults = textResults
        )

        bodyHtml = self.__email.bodyHtml.format(
            lastName = lastName,
            schedDate = date,
            htmlResults = htmlResults,
            logoUrl = logo
        )

        self.__alternative.attach(MIMEText(bodyText, 'plain'))
        self.__alternative.attach(MIMEText(bodyHtml, 'html'))

        self.__message.attach(self.__alternative)
        self.__attachDoc(attachmentPath)
    
    def sendEmail(self):
        try:
            toAddr = []
            if self.__message['To']:
                toAddr += [addr.strip() for addr in self.__message['To'].split(',')]
            if self.__Bcc:
                self.__Bcc = ','.join(self.__Bcc)
                toAddr += [addr.strip() for addr in self.__Bcc.split(',')]

            with smtplib.SMTP(self.__SMTPServer, self.__SMTPPort) as server:
                server.starttls()
                server.login(self.__senderEmail, self.__password)
                server.send_message(self.__message, from_addr = self.__senderEmail, to_addrs = toAddr)
            self.__logger.info(f"Email sent to {self.__message['To']}")
        except Exception as e:
            self.__logger.error(f"Failed to send email to {self.__message['To']} - {e}")