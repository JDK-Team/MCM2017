from Person import Person
import time

class Node:
    def __init__(self, time, function, adjacencyList, isEnd):
        self.queue = []
        self.timeAtNode = time
        self.choiceFunction = function #returns integer that is index of node in adjacency list
        self.adjacencyList = adjacencyList
        self.isSimulating = False
        self.isEnd = isEnd

    def addToQueue(self, person): #add person to end of array, front of queue is front of array
        if(self.isEnd):
            print(person.timeSpent)
            return
        self.queue.append(person)
        person.startWaiting();
        if(not(self.isSimulating)):
            self.startSimulation()

    def startSimulation(self):
        self.isSimulating = True
        while(len(self.queue)>0):
            person = self.queue.pop(0)
            time.sleep(self.timeAtNode)
            person.endWaiting()
            nodeIndex = self.choiceFunction()
            self.adjacencyList[nodeIndex].addToQueue(person)
        self.isSimulating = False
