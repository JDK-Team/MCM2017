import time
scalar = 1000

class Person:
    counter = 1
    def __init__(self):
        self.timeSpent = 0
        self.timesAtNodes = []
        self.id = Person.counter
        Person.counter += 1
        self.path = []
        self.queuesAtNodes = []
        self.precheck = 0 #0 means not precheck, 1 means precheck

    def startWaiting(self):
        self.startTime = time.time()

    def endWaiting(self):
        self.endTime = time.time()
        diff = (self.endTime - self.startTime)*scalar
        self.timeSpent += diff
        self.timesAtNodes.append(diff)
