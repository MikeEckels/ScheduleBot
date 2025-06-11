import os
import sys
import logging
from Browser import Browser
from PDFSearch import Extractor
from EmailClient import EmailClient
from datetime import datetime, timedelta
from AddressBook import AddressBookBuilder

sentLog = os.path.abspath("sentLog.txt")
addresses = os.path.abspath("addresses.json")
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level = logging.INFO,
                    datefmt = '%m/%d %H:%M'
)

def checkFinished(days):
    if os.path.exists(sentLog):
        with open(sentLog, "r") as f:
            sentDates = [date.strip() for date in f.read().split(',')]
            dateStrings = [day.strftime("%Y-%m-%d") for day in days]
        if any(date in dateStrings for date in sentDates):
            logger.info("Emails already sent for today. Exiting.")
            sys.exit(0)
        else:
            with open(sentLog, "w") as f: pass
            addressBook.clearAllNotified()
            addressBook.save(addresses)

if __name__ == '__main__':
    emailsSent = set()
    browser = Browser()
    extractor = Extractor()
    emailClient = EmailClient()
    addressBook = AddressBookBuilder()

    tomorrow = (datetime.now() + timedelta(days = 1))
    sunday = tomorrow + timedelta(days = 1)
    monday = tomorrow + timedelta(days = 2)
    isWeekend = True if tomorrow.weekday() == 5 else False

    addressBook.load(addresses)

    days = [tomorrow, sunday, monday] if isWeekend else [tomorrow]
    checkFinished(days)

    for entry in addressBook.getActiveEntries()[:]:
        name = entry.name
        squadron = entry.squadron
        logo = extractor.getLogo(squadron)

        for day in days:
            date = day.strftime("%B %d, %Y")
            sentEmail = (name, squadron, day)
            pdfPath = browser.downloadSched(squadron, day)

            if pdfPath:
                results = extractor.search(pdfPath, [name])
                recipients = entry.getToList()
                emailClient.createEmail(
                    to = recipients,
                    date = date,
                    logo = logo,
                    searchResults = results,
                    attachmentPath = pdfPath
                )
                logger.info(f'Sending email to: {recipients}')
                emailClient.sendEmail()
                emailsSent.add(sentEmail)
            else:
                logger.warning(f"Failed to download schedule for {squadron} on {day}")

        if all((name, squadron, day) in emailsSent for day in days):
            addressBook.removeEntry(entry)
            addressBook.save(addresses)
            logger.info(f'Removed: {entry.name}')
        
    if not addressBook.getActiveEntries():
        with open(sentLog, "a") as f:
            for day in days:
                f.write(f'{day.strftime("%Y-%m-%d")},')
            logger.info("All emails sent")