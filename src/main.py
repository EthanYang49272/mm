import logging

from src.modes.StopWatch import StopWatch
from src.config import CONFIG

logging.basicConfig(filename='mm.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def menu():
    print("*****Menu*****")
    while True:
        logging.debug("Waiting for user's selection")
        choice = input("Select a mode: \nStopWatch[1]\nTimer[2]\nZen[3]\nSettings[4]\n")
        logging.debug("User selected mode %s" % choice)
        try:
            if choice == '1':
                StopWatch(CONFIG["stopwatch_duration"])
            elif choice == '2':
                Timer()
            elif choice == '3':
                Zen()
            elif choice == '4':
                Settings()
            break
        except:
            print("Please enter a valid number")
    

def Timer():
    ...

def Zen():
    ...

def Settings():
    ...

# python3 -u -m mm.main
# cd ../

menu()