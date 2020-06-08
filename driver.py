from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox


class Browser(Firefox):
    def __init__(self, settings):
        self.settings = settings

        self.fopt = Options()
        self.fopt.add_argument("--headless")
        super().__init__(executable_path="./geckodriver.exe", firefox_options=self.fopt)

        self.login_url = self.settings["login_url"]

        self.login()

    def login(self):
        self.get(self.login_url)
        while True:
            try:
                self.find_element_by_id("ctl00_txtUsername").send_keys(self.settings["username"])
                self.find_element_by_id("ctl00_txtPassword").send_keys(self.settings["password"])
                self.execute_script('javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions('
                                           '"ctl00$ctl01", "", true, "Login", "", false, true))')
                break
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(1)

        while True:
            try:
                self.find_element_by_id("ctl00_cntrlRoleSelection_lnkAdmin")
                break
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(1)