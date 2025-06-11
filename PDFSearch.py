import logging
import pdfplumber

class Extractor():
    def __init__(self):
        self.__reset()
    
    def __reset(self):
        self.__logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level = logging.INFO,
                    datefmt = '%m/%d %H:%M'
        )

        self.__ranks = [
            "ENS", "LT", "LCDR", "CAPT", "LTCOL", "CAPT", "CDR",
            "2NDLT", "LTJG", "MAJ", "CIV", "1STLT", "1LT", "2LT"
        ]

        self.__logos = {
            "VT-2" : "https://www.cnatra.navy.mil/tw5/vt2/assets/img/logo-footer.png",
            "VT-3" : "https://www.cnatra.navy.mil/tw5/vt3/assets/img/logo-footer.png",
            "VT-6" : "https://www.cnatra.navy.mil/tw5/vt6/assets/img/logo-footer.png"
        }
    
    def __nameParts(self, name):
        return [part.strip().upper() for part in name.replace("#", "").split(",") if part.strip()]

    def __assemble(self, matches, nameParts):
        #ip, student, _ = matches[1].partition(nameParts[1])
        try:
            index = matches[0][1].index(nameParts[0])
            match = [(matches[0][0], matches[0][1][:index] + matches[1][1] + matches[0][1][index:])]
        except:
            match = []
        return match
    
    def getLogo(self, squadron):
        return self.__logos.get(squadron)
    
    def search(self, PDFPath, names):
        self.__reset()
        results = {}

        for name in names:
            matches = []
            namep = self.__nameParts(name)
            with pdfplumber.open(PDFPath) as pdf:
                for pageNum, page in enumerate(pdf.pages, start = 1):
                    text = page.extract_text()
                    if not text:
                        continue

                    lines = text.splitlines()

                    for line in lines:
                        line = line.strip().upper()
                        if any(part in line for part in namep if part.upper() not in self.__ranks):
                            matches.append((pageNum, line))

            usedParts = {}
            for matchIndex, match in enumerate(matches):
                for partIndex, part in enumerate(namep):
                    if part in match[1]:
                        usedParts[matchIndex] = partIndex

            prevVal = -1
            deleteKeys = []
            for index, value in enumerate(usedParts.values()):
                if not value >= prevVal:
                    deleteKeys.append(index)

                if value == prevVal:
                    deleteKeys.append(index - 1)

                prevVal = value

            for i in sorted(deleteKeys, reverse = True):
                del matches[i]

            result = self.__assemble(matches, namep)
            self.__logger.info(f'Found possible match for {name}: {result}')
            results[name] = {"matches" : result}

        return results