from Person import Person
import time
import sys
import threading

thread_trace = []

class Node(threading.Thread):
    def __init__(self, time, function, adjacencyList, defaultChoiceIndex, queueMax, name):
        threading.Thread.__init__(self, name=name)
        self.queue = []
        self.name = name
        self.timeAtNode = time
        self.choiceFunction = function #returns integer that is index of node in adjacency list
        self.adjacencyList = adjacencyList
        self.defaultChoiceIndex = defaultChoiceIndex
        self.isSimulating = False
        self.queueMax = queueMax
        self.shouldFinish = threading.Event()
        self.shouldWork = threading.Event()

    def addToQueue(self, person):#add person to end of array, front of queue is front of array
        if (len(self.queue)>= self.queueMax ):
            return False
        
        person.queuesAtNodes.append(len(self.queue))
        self.queue.append(person)
        person.endWaiting()
        print("start", self.name, person.id)
        person.path.append(self.name)
        self.shouldWork.set()
        return True
        #if(not(self.isSimulating))

    def startSimulation(self):
        # self.isSimulating = True
        while(len(self.queue)>0):
            person = self.queue.pop(0)
            time.sleep(self.timeAtNode)
            #person.endWaiting()
            queueLengths = list(map(lambda n: len(n.queue), self.adjacencyList))

            nodeIndex = self.choiceFunction(queueLengths,self.defaultChoiceIndex)
            while (True):
                if (self.adjacencyList[nodeIndex].addToQueue(person)):
                    person.startWaiting()
                    #print("end", self.name, person.id)
                    break

        # self.isSimulating = False

    def run(self):
        while not self.shouldFinish.is_set():
            #thread_trace.append(self.name)#this will really cause it to slow down, but might give info
            self.shouldWork.wait()
            self.startSimulation()
            self.shouldWork.clear()
    
    def stop(self):
        for node in self.adjacencyList:
            node.stop()
        self.shouldWork.set() # just in case the thread is waiting at the time this is called
        self.shouldFinish.set()

    def __str__(self):
        return self.name



class EndNode(Node):
    def __init__(self):
        Node.__init__(self, 0, None, None, 0, 1000, "end")
        self.count = 0
        self.numPeople = 0
        self.graph = None

    def addToQueue(self, person):
        person.endWaiting()
        print("Person", person.id,"finished:",person.timeSpent)
        print(person.path)
        print(person.queuesAtNodes)
        print(list(map(lambda x: round(x,2), person.timesAtNodes)))
        with open("people_times.csv", 'a') as peoplecsv:
            peoplecsv.write('{},{},{}\n'.format(person.id,person.timeSpent,person.timesAtNodes,sep=','))
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
