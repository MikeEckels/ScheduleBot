import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Browser:
    def __init__(self, clearDownloads = True):
        self.__logger = logging.getLogger(__name__)
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                            level = logging.INFO,
                            datefmt = '%m/%d %H:%M'
        )

        self.__trainingWing = "5"
        self.__downloadTimeout = 60
        self.__downloadDir = os.path.abspath("downloads")
        os.makedirs(self.__downloadDir, exist_ok = True)
        self.__siteURL = "https://www.cnatra.navy.mil/scheds/default.asp?sq=trawing%205"

        self.__service = webdriver.ChromeService(log_output = 'NUL')
        self.__options = webdriver.ChromeOptions()
        self.__options.add_experimental_option("prefs", {
            "download.default_directory": self.__downloadDir,
            "plugins.always_open_pdf_externally": True,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        self.__options.add_argument("--headless=new")
        self.__options.add_argument("--disable-gpu")
        self.__options.add_argument("--no-sandbox")
        self.__options.add_argument("--disable-dev-shm-usage")
        self.__options.add_argument("--log-level=3")
        self.__options.add_argument("--disable-logging")
        self.__options.add_argument("--disable-extensions")

        if clearDownloads: self.__clearDownloads()
    
    def __checkDuplicates(self, pdfPath, clean = False):
        if os.path.exists(pdfPath):
            try:
                if clean:
                    os.remove(pdfPath)
                    self.__logger.info(f"Deleted {pdfPath}")
                    return False
                else:
                    return True
            except Exception as e:
                self.__logger.exception(e)
    
    def __clearDownloads(self):
        for file in os.listdir(self.__downloadDir):
            if file.lower().endswith(".pdf"):
                filePath = os.path.join(self.__downloadDir, file)
                try:
                    os.remove(filePath)
                    logging.info(f"Deleted: '{file}'")
                except Exception as e:
                    logging.warning(f"Failed to delete: '{file}' - {e}")
    
    def __waitAndSelectByVal(self, driver, id, value, wait):
        wait.until(EC.element_to_be_clickable((By.ID, id)))

        def __optionPresent(driver):
            select = Select(driver.find_element(By.ID, id))
            return any(opt.get_attribute("value") == value for opt in select.options)

        wait.until(__optionPresent)
        Select(driver.find_element(By.ID, id)).select_by_value(value)
    
    def downloadSched(self, squadron, date):
        pdfName = f"!{date.strftime("%Y-%m-%d")}!{squadron}!Frontpage.pdf"
        pdfPath = os.path.join(self.__downloadDir, pdfName)
        searchDate = date.strftime("%#m/%#d/%Y")
        if self.__checkDuplicates(pdfPath): return pdfPath

        with webdriver.Chrome(options = self.__options, service = self.__service) as driver:
            wait = WebDriverWait(driver, 10)
            try:
                self.__logger.info(f"Opening schedule site for: {searchDate}")
                driver.get(self.__siteURL)

                self.__waitAndSelectByVal(driver, "ddlWing", self.__trainingWing, wait)
                self.__waitAndSelectByVal(driver, "ddlSchedsW5", squadron, wait)
                self.__waitAndSelectByVal(driver, "ddlDate", searchDate, wait)
                
                notAvailableDiv = driver.find_element(By.ID, "divNotFound")
                if notAvailableDiv.is_displayed():
                    self.__logger.warning("Schedule not available")
                else:
                    wait.until(EC.element_to_be_clickable((By.ID, "btnFrontPage"))).click()
                    self.__logger.info("Schedule available. Downloading PDF")
                    startTime = time.time()
                    while not os.path.exists(pdfPath):
                        if time.time() - startTime > self.__downloadTimeout:
                            self.__logger.warning("Timeout: Download took too long")
                            break
                        time.sleep(1)

            except Exception as e:
                self.__logger.exception(e)
        
        return pdfPath if os.path.exists(pdfPath) else False
        
    def getSchedulePaths(self):
        pdfFiles = [f for f in os.listdir(self.__downloadDir) if f.lower().endswith(".pdf")]
        pdfPaths = [os.path.join(self.__downloadDir, f) for f in pdfFiles]

        if not pdfPaths:
            self.__logger.warning("No PDF's downloaded")
            
        return pdfPaths