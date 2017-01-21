from Person import Person
import time
import sys
import threading

class Node(threading.Thread):
    def __init__(self, time, function, adjacencyList, queueMax, name):
        threading.Thread.__init__(self, name=name)
        self.queue = []
        self.name = name
        self.timeAtNode = time
        self.choiceFunction = function #returns integer that is index of node in adjacency list
        self.adjacencyList = adjacencyList
        self.isSimulating = False
        self.queueMax = queueMax
        self.shouldFinish = threading.Event()

    def addToQueue(self, person):#add person to end of array, front of queue is front of array
        if (len(self.queue)>= self.queueMax ):
            return False
        self.queue.append(person)
        #print("start", self.name, person.id)
        return True
        #if(not(self.isSimulating))

    def startSimulation(self):
        # self.isSimulating = True
        while(len(self.queue)>0):
            person = self.queue.pop(0)
            time.sleep(self.timeAtNode)
            #person.endWaiting()
            nodeIndex = self.choiceFunction()
            while (True):
                if (self.adjacencyList[nodeIndex].addToQueue(person)):
                    #person.endWaiting()
                    #print("end", self.name, person.id)
                    break

        # self.isSimulating = False

    def run(self):
        while not self.shouldFinish.is_set():
            self.startSimulation()
    
    def stop(self):
        for node in self.adjacencyList:
            node.stop()
        self.shouldFinish.set()
    
    def __str__(self):
        return self.name



class EndNode(Node):
    def __init__(self):
        Node.__init__(self, 0, None, None, 1000, "end")
        self.count = 0
        self.numPeople = 0
        self.graph = None

    def addToQueue(self, person):
        person.endWaiting()
        print(person.timeSpent)
        self.count += 1
        if(self.count == self.numPeople):
            self.graph.finish()
        return True

    def stop(self):
        self.shouldFinish.set()
    

# class StartNode(Node):
#     def __init__(self, time, function, adjacencyList):
#         Node.__init__(self, time, function, adjacencyList)
#     def addToQueue(self, person):
#         for node in self.adjacencyList:
#             if(len(node.queue)==0):
#                 node.addToQueue(person)
