
class TextClient:
    def __init__(self):
        self.__carrierMap = {
            "verizon": "vtext.com",
            "tmobile": "tmomail.net",
            "sprint": "messaging.sprintpcs.com",
            "at&t": "txt.att.net",
            "boost": "smsmyboostmobile.com",
            "cricket": "sms.cricketwireless.net",
            "uscellular": "email.uscc.net",
            "googlefi": "msg.fi.google.com",
        }

    def toEmail(self, numberCarrierList):
        addresses = []
        for numberCarrier in numberCarrierList:
            number, carrier = numberCarrier

            emailAddr = self.__carrierMap.get(carrier)
            emailAddr = None if emailAddr is None else f"{number}@{emailAddr}"
            addresses.append(emailAddr)
        return addresses