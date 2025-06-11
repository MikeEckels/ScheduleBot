import re
import json
from Texting import TextClient
from typing import List, Optional, Union
from dataclasses import dataclass, field, asdict

@dataclass
class BookEntry:
    name: str
    squadron: str
    email: List[str]
    notified: bool = False
    number: Optional[List[List[Union[int, str]]]] = None
    text: TextClient = field(default_factory = TextClient, repr = False, compare = False)
    
    def getToList(self):
        emails = ", ".join(self.email)
        if not self.number: return [self.name, emails]
        numbers = ", ".join(self.text.toEmail(self.number))
        recipients = f"{emails}, {numbers}".split(',')
        to = recipients[0].strip()
        bcc = ','.join(recipient.strip() for recipient in recipients[1:])
        return [self.name, to, bcc]

    def toDict(self):
        dict = asdict(self)
        dict.pop("text", None)
        return dict

class AddressBookBuilder:
    def __init__(self):
        self.__entries = []
    
    def __getAllEntriesAsDict(self):
        return [entry.toDict() for entry in self.__entries]

    def addEntry(self, entry):
        self.__entries.append(entry)
    
    def removeEntry(self, entry):
        if entry in self.__entries:
            entry.notified = True
    
    def clearAllNotified(self):
        for entry in self.__entries:
            entry.notified = False
    
    def load(self, jsonFile):
        with open(jsonFile, 'r') as f:
            addresses = json.load(f)
        for entry in addresses:
            entry.setdefault("notified", False)
            self.addEntry(BookEntry(**entry))
    
    def save(self, jsonFile):
        entries = self.__getAllEntriesAsDict()
        jsonData = json.dumps(entries, indent = 2)
        jsonData = re.sub(
            r'\[\s+((?:"[^"]+",?\s*)+)\s+\]',
            lambda m: '[' + ''.join(m.group(1).split()) + ']',
            jsonData
        )

        jsonData = re.sub(
            r'\[\s+((?:\[[^\[\]]+\],?\s*)+)\s+\]',
            lambda m: '[' + ' '.join(line.strip() for line in m.group(1).splitlines()) + ']',
            jsonData
        )

        with open(jsonFile, 'w') as f:
            f.write(jsonData)
    
    def getActiveEntries(self):
        return [entry for entry in self.__entries if not entry.notified]