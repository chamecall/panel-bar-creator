class Clock:
    def __init__(self, time: str):
        print('time:',time)
        self.min, self.sec, self.msec = (int(value) for value in time.split(':'))
        self.total_msecs = self.get_total_msecs()


    def get_total_msecs(self):
        return self.min * 60000 + self.sec * 1000 + self.msec