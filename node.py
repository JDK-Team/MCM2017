from Person import Person
import time
import sys
import threading

#thread_trace = []

class Node(threading.Thread):
    def __init__(self, timeFunction, function, adjacencyList, defaultChoiceIndex, queueMax, name):
        threading.Thread.__init__(self, name=name)
        self.queue = []
        self.name = name
        self.timeFunction = timeFunction
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
        #print("start", self.name, person.id)
        person.path.append(self.name)
        self.shouldWork.set()
        return True
        #if(not(self.isSimulating))

    def startSimulation(self):
        # self.isSimulating = True
        while(len(self.queue)>0):
            person = self.queue.pop(0)
            time.sleep(self.timeFunction(person.path))
            #person.endWaiting()
            queueLengths = list(map(lambda n: len(n.queue), self.adjacencyList))

            nodeIndex = self.choiceFunction(queueLengths,self.defaultChoiceIndex, person.path)
            while (True):
                if (self.adjacencyList[nodeIndex].addToQueue(person)):
                    person.startWaiting()
                    #print("end", self.name, person.id)
                    break
                # else:
                #     print("person ", person.id, " is waiting at ", self.name, "the next queue has length: ", queueLengths[nodeIndex])

        # self.isSimulating = False

    def run(self):
        while not self.shouldFinish.is_set(): #so that program will end when you want it to
            #thread_trace.append(self.name)#this will really cause it to slow down, but might give info
            self.shouldWork.wait()
            self.startSimulation()
            self.shouldWork.clear()
    
    def stop(self): #ends the program
        for node in self.adjacencyList:
            node.stop()
        self.shouldWork.set() # just in case the thread is waiting at the time this is called
        self.shouldFinish.set()

    def __str__(self):
        return self.name



class EndNode(Node):
    def __init__(self, filename):
        Node.__init__(self, 0, None, None, 0, 1000, "end")
        self.count = 0
        self.numPeople = 0
        self.graph = None
        self.filename = filename

    def addToQueue(self, person):
        person.endWaiting()
        print("Person", person.id,"finished:",person.timeSpent)
        print(person.path)
        #print(person.queuesAtNodes)
        print(list(map(lambda x: round(x,2), person.timesAtNodes)))
        newPersonTimes = self.formatPerson(person.timesAtNodes, person.path)
        with open(self.filename, 'a') as peoplecsv:
            peoplecsv.write('{},{},'.format(person.id,person.timeSpent,sep=','))
            for time in newPersonTimes:
                peoplecsv.write('{},'.format(time, sep=','))
            peoplecsv.write('{}\n'.format(person.precheck, sep=','))
        self.count += 1
        if(self.count == self.numPeople):
            print("done")
            self.graph.finish()
        return True

    def formatPerson(self, timeAtNodeInfo, path):
        newNodeInfo = timeAtNodeInfo.copy()
        del newNodeInfo[0]
        #see if it contains zoneDpatdown
        if("zoneDpatdown" not in path[4]):
            newNodeInfo.insert(4, 0)
            if(len(path) == 5):
                newNodeInfo.append(0)
        elif(len(path) == 6):
            newNodeInfo.append(0)
        newNodeInfo = list(map(lambda x: round(x,3), newNodeInfo))
        return newNodeInfo


    def stop(self):
        self.shouldWork.set()
        self.shouldFinish.set()


# class StartNode(Node):
#     def __init__(self, time, function, adjacencyList):
#         Node.__init__(self, time, function, adjacencyList)
#     def addToQueue(self, person):
#         for node in self.adjacencyList:
#             if(len(node.queue)==0):
#                 node.addToQueue(person)
