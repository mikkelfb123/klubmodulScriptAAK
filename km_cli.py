import json

from driver import Browser
from klubmodul_deleter import KlubModulDeleter
from klubmodul_writer import KlubModul

class Main:
    def __init__(self):
        self.settings = json.load(open("settings.json", 'r'))

        inp = input("Delete(d) all events/Write(w) from settings")
        if inp in ["D", "d", "Delete", "delete"]:
            self.delete_all_events()
        elif inp in ["W", "w", "Write", "write"]:
            self.writer()


    def writer(self):
        print("Bekræft følgende indstillinger: ")
        [print(k, ": ", v) for k, v in self.settings.items()]

        if input("Y/n\n") not in ["Y", "y"]:
            print("ret instillinger og prøv igen")
            return
        else:
            self.d = Browser(self.settings)
            KlubModul(settings=self.settings, driver=self.d)

    def delete_all_events(self):
        self.d = Browser(settings=self.settings)
        KlubModulDeleter(settings=self.settings, driver=self.d)


if __name__ == "__main__":
    m = Main()
