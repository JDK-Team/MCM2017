import time

class Person:
    counter = 1
    def __init__(self):
        self.timeSpent = 0
        self.id = Person.counter
        Person.counter += 1

    def startWaiting(self):
        self.startTime = time.time()

    def endWaiting(self):
        self.endTime = time.time()
        self.timeSpent += self.endTime - self.startTime