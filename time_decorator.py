import time
from datetime import datetime


class TimeDecorator:
    def __init__(self, func):
        self.func = func
        today = datetime.today()
        self.time1 = datetime(today.year, today.month, today.day, 9, 30)
        self.time2 = datetime(today.year, today.month, today.day, 11, 30)
        self.time3 = datetime(today.year, today.month, today.day, 13, 00)
        self.time4 = datetime(today.year, today.month, today.day, 14, 59)
        self.klt = 5

    def __call__(self, *args, **kwargs):
        now = datetime.now()

        # before trading hours, sleep
        if now < self.time1:
            print('waiting for markets to open...')
            sleep_seconds = (self.time1 - now).total_seconds()
            time.sleep(sleep_seconds)

        # after trading hours, exit
        if now > self.time4:
            print('exit program...')
            exit(0)

        # lunch break
        if self.time2 < now < self.time3:
            print('lunch break...')
            sleep_seconds = (self.time3 - now).total_seconds()
            time.sleep(sleep_seconds)

        # following code ensures the function gets called at every 5-minute time point
        print('waiting for the next 5-minute data...')
        cycle_seconds = (self.klt - datetime.now().minute % self.klt) * 60 - datetime.now().second
        time.sleep(cycle_seconds)

        return self.func(*args, **kwargs)

