import time
scalar = 100

#Represents a person that travels through the TSA security graph
class Person:
    counter = 1 #counts the number of people that have been created (static variable)
    def __init__(self):
        """Creates a new person object"""
        self.timeSpent = 0
        self.timesAtNodes = []
        self.id = Person.counter
        Person.counter += 1
        self.path = []
        self.queuesAtNodes = []
        self.precheck = 0 #0 means not precheck, 1 means precheck

    def startWaiting(self):
        """The person has started waiting in line at a node"""
        self.startTime = time.time()

    def endWaiting(self):
        """The person is done waiting in line at that node (records how long they were there)"""
        self.endTime = time.time()
        diff = (self.endTime - self.startTime)*scalar
        self.timeSpent += diff
        self.timesAtNodes.append(diff)
