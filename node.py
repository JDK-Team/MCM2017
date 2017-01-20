from Person import Person

class Node:
    def __init__(self, time, function):
        self.queue = []
        self.timeAtNode = time
        self.choiceFunction = function

    def addToQueue(self, person): #add person to end of array, front of queue is front of array
        self.queue.append(person)