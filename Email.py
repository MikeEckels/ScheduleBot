from dataclasses import dataclass

@dataclass
class Email():
    subject: str = ("Flight Schedule for {schedDate}: {lastName}")
    bodyText: str = (
            "Hello {lastName},\n"
            "The schedule for {schedDate} has been posted.\n\n"
            "Relevant entries (must verify):\n"
            "{textResults}\n\n"
            "Best regards,\nAutomated Scheduler Bot"
        )

    bodyHtml: str = """\
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
              <div style="text-align: center; margin-bottom: 20px;">
                <img src="{logoUrl}" alt="VT-6 Shooters Logo" style="max-width: 120px; height: auto;">
              </div>
              <h2 style="color: #003366; margin-bottom: 20px;">Flight Schedule Notification</h2>
              <p style="font-size: 16px; color: #333; margin-bottom: 5px;">Hello <b>{lastName}</b>,</p>
              <p style="font-size: 16px; color: #333; margin-top: 0;">The schedule for <b>{schedDate}</b> has been posted.</p>
              <p style="font-size: 16px; color: #333;"><b>Relevant entries:</b> (must verify)</p>
              <ul style="font-size: 16px; color: #333; padding-left: 20px; margin-top: 10px; margin-bottom: 20px;">
                {htmlResults}
              </ul>
              <p style="font-size: 16px; color: #333;">The full schedule PDF is attached.</p>
              <hr style="margin: 5px 0;">
              <p style="font-size: 14px; color: #888;">This email was sent automatically by your Flight Scheduler Bot.</p>
            </div>
          </body>
        </html>"""