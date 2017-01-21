import time

class Person:
    counter = 1
    def __init__(self):
        self.timeSpent = 0
        self.timesAtNodes = []
        self.id = Person.counter
        Person.counter += 1
        self.path = []
        self.queuesAtNodes = []

    def startWaiting(self):
        self.startTime = time.time()

    def endWaiting(self):
        self.endTime = time.time()
        self.timeSpent += self.endTime - self.startTime
        self.timesAtNodes.append(self.endTime - self.startTime)
