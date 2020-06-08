from time import sleep

import bs4
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, JavascriptException


class KlubModulDeleter:
    def __init__(self, settings, driver):
        self.settings = settings
        self.driver = driver
        self.events = []
        self.booking_url = self.settings["booking_url"]
        self.delete_all_events()

    def delete_all_events(self):
        self.driver.get(self.booking_url)
        soup = bs4.BeautifulSoup(self.driver.page_source, 'lxml')

        while True:
            events = soup.find_all("a", {"class": "km-slet tooltip"})
            if len(soup.find_all("a", {"class": "dataTables_empty"})) == 0:
                return

            print("delete event")
            self.delete_element(events[0]['href'].replace("javascript:", ""))





    def delete_element(self, script):
        while True:
            try:
                self.driver.find_element_by_id("30sbook")
                self.driver.execute_script("document.getElementById('30sbook').style.display = 'none';")
                break
            except (NoSuchElementException, StaleElementReferenceException, JavascriptException):
                sleep(0.1)

        self.driver.execute_script(script)
        sleep(1)


    def read_events(self):
        soup = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
        table = soup.find({"id": "bookingMaintenanceOverview"})
        thead = table.find("thead")
        headers = [n.text for n in thead.find("tr").find_all("td")]
        print(headers)

        tbody = table.find("tbody")

        print(tbody)
        trs = tbody.find_all("tr")
        for tr in trs:
            row_dict = {}
            tds = tr.find_all("td")
            for i in range(len(tds)):
                row_dict[headers[i]] = tds[i]

            self.events.append(row_dict)

    def get_events(self):
        return self.events
