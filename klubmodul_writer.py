from datetime import datetime, timedelta, time
from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys


class KlubModul:
    def __init__(self, settings, driver):
        self.settings = settings

        self.driver = driver
        self.start_datetime = datetime.strptime(self.settings["start_date"] + "-{hours}-{minutes}".format(
            hours=self.settings["start_hour"], minutes=self.settings["start_minute"]), '%d-%m-%Y-%H-%M')
        self.end_datetime = datetime.strptime(self.settings["end_date"] + "-{hours}-{minutes}".format(
            hours=self.settings["end_hour"], minutes=self.settings["end_minute"]), '%d-%m-%Y-%H-%M')

        self.booking_url = self.settings["booking_url"]
        self.events = []
        self.generate_events()
        self.create_events_online()


    def generate_events(self):
        events = []

        event_start_datetime = self.start_datetime
        #tjekker datointerval
        while event_start_datetime <= self.end_datetime:
            #tjekker event inden for åbningstider
            if (event_start_datetime.time() > time(hour=self.settings["end_hour"], minute=self.settings["end_hour"])):
                continue

            #Hvornår stopper eventet
            event_end_datetime = event_start_datetime + timedelta(hours=self.settings["duration_hours"],
                                                                  minutes=self.settings["duration_minutes"])
            events.append({
                "start_datetime": event_start_datetime,
                "end_datetime": event_end_datetime,
                "headcount": self.settings["headcount"],
                "max_waiting_list": self.settings["max_waiting_list"]
            })

            #increase event_start_datetime
            event_start_datetime += timedelta(minutes=self.settings["arrival_interval_minutes"])

        print(events)
        self.events = events

    def create_event(self, event):
        self.new_window()
        self.driver.get(self.booking_url)
        print(event)

        while True:
            try:
                self.driver.find_element_by_id("30sbook")
                self.driver.execute_script("document.getElementById('30sbook').style.display = 'none';")
                break
            except (NoSuchElementException, StaleElementReferenceException):
                sleep(1)

        #Overskrift
        self.driver.find_element_by_id("ctl00_ContentPlaceHolderBody_txtName").send_keys('Coronaklatring')

        #Område
        area = self.driver.find_element_by_id("ctl00_ContentPlaceHolderBody_ddPool_chosen")
        area.click()
        self.wait_by_element_class_name(area, "chosen-results")
        area.find_element_by_class_name("chosen-results").click()

        #Dato
        date = self.driver.find_element_by_id("ctl00_ContentPlaceHolderBody_txtStartDate")
        date.clear()
        date_str = event["start_datetime"].strftime("%d-%m-%Y")
        date.send_keys(date_str)
        date.send_keys(Keys.ENTER)


        #start hours
        self.set_time("ctl00_ContentPlaceHolderBody_ddStartHour_chosen", event["start_datetime"].hour)

        #start_minutes
        self.set_time("ctl00_ContentPlaceHolderBody_ddStartMinute_chosen", event["start_datetime"].minute)

        # end_hours
        self.set_time("ctl00_ContentPlaceHolderBody_ddEndHour_chosen", event["end_datetime"].hour)

        # end_minutes
        self.set_time("ctl00_ContentPlaceHolderBody_ddEndMinute_chosen", event["end_datetime"].minute)

        # max participants
        self.driver.find_element_by_id("ctl00_ContentPlaceHolderBody_txtMaxNumberEnrollment").send_keys(event["headcount"])

        # max waiting list
        self.driver.find_element_by_id("ctl00_ContentPlaceHolderBody_txtMaxNumberWaitinglist").send_keys(event["max_waiting_list"])

        #instructor
        ins = self.driver.find_element_by_id("ctl00_ContentPlaceHolderBody_ddInstructor_chosen")
        ins.click()
        self.wait_by_element_class_name(ins, "chosen-results")
        ins.find_element_by_class_name("chosen-results").click()

        #send + ref for testing if send properly
        ref = self.driver.find_element_by_id("bookingMaintenanceOverview").find_element_by_tag_name("tbody").find_elements_by_tag_name("tr")
        self.driver.execute_script('WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions('
                                   '"ctl00$ContentPlaceHolderBody$btnSave", "", true, "valGroupTeam", "", false, '
                                   'true))')

        #sleep until send
        #Skal teste om det RIGTIGE event kommer på.

        while True:
            try:
                post_ref = self.driver.find_element_by_id("bookingMaintenanceOverview").find_element_by_tag_name(
                "tbody").find_elements_by_tag_name("tr")
                if len(ref) == len(post_ref):
                    break

            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
                sleep(1)


        self.close_window()


    def new_window(self):
        #ActionChains(self.driver).key_down(Keys.CONTROL).key_down("n").key_up(Keys.CONTROL).key_up("n")
        self.driver.execute_script("window.open()")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return self.driver.window_handles[-1]

    def close_window(self):
        #ActionChains(self.driver).key_down(Keys.CONTROL).key_down("w").key_up(Keys.CONTROL).key_up("w")
        self.driver.execute_script("window.close()")
        self.driver.switch_to.window(self.driver.window_handles[0])
        return self.driver.window_handles[0]

    def set_time(self, element_id, value):
        while True:
            try:
                h = self.driver.find_element_by_id(element_id)
                h.click()
                hin = h.find_element_by_tag_name("input")
                hin.send_keys(str(value))
                hin.send_keys(Keys.ENTER)
                break
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
                sleep(1)

    def wait_by_element_id(self, parent, element_id):
        while True:
            try:
                el = parent.find_element_by_id(element_id)
                return el
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
                sleep(0.1)

    def wait_by_element_class_name(self, parent, element_class_name):
        while True:
            try:
                el = parent.find_element_by_class_name(element_class_name)
                return el
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
                sleep(0.1)

    def create_events_online(self):
        for ev in self.events:
            print("Creating: ", str(ev["start_datetime"]))
            self.create_event(ev)
            print("Done with: ", str(ev["start_datetime"]))



