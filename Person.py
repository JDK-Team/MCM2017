import time
scalar = 100

class Person:
    counter = 1
    def __init__(self):
        self.timeSpent = 0
        self.timesAtNodes = []
        self.id = Person.counter
        Person.counter += 1
        self.path = []

    def startWaiting(self):
        self.startTime = time.time()

    def endWaiting(self):
        self.endTime = time.time()
        diff = (self.endTime - self.startTime)*scalar
        self.timeSpent += diff
        self.timesAtNodes.append(diff)
