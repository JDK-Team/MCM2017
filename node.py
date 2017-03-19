from Person import Person
import time
import sys
import threading
scalar = 100
count = 1

#A class whose objects represent nodes in the TSA security graph. Extends threading.Thread because each node is its
#own thread - this allows for real-time simulation.
class Node(threading.Thread):
    def __init__(self, timeFunction, function, adjacencyList, defaultChoiceIndex, queueMax, name):
        """
        Creates a new node with the given parameters.
        :param timeFunction: function that determines the amount of time a passenger spends at that node
        :param function: function that determines which node the passenger will choose next
        :param adjacencyList: list of all the nodes the passenger could choose to go next
        :param defaultChoiceIndex: index of the passenger's default choice node (usually the one directly in front of them)
        :param queueMax: maximum length of the queue at this node
        :param name: name of the node
        """
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

    def addToQueue(self, person):
        """
        Adds a person to the end of the list that is the queue at the node.
        :param person: person to be added to the queue
        :return: true if the person is successfully added, false otherwise (cannot be added if that would case the queue
        to go over its maximum length)
        """
        if (len(self.queue)>= self.queueMax ):
            return False
        
        person.queuesAtNodes.append(len(self.queue))
        self.queue.append(person)
        person.endWaiting()
        person.path.append(self.name)
        self.shouldWork.set()
        return True

    def startSimulation(self):
        """
        Starts simulating the flow of passengers through the node.
        """
        # self.isSimulating = True
        while(len(self.queue)>0):
            person = self.queue.pop(0)
            time.sleep(self.timeFunction(person.path)) #wait for the person to finish doing their business at the front of the line
            queueLengths = list(map(lambda n: len(n.queue), self.adjacencyList))

            nodeIndex = self.choiceFunction(queueLengths,self.defaultChoiceIndex, person.path) #index of the next node the passenger will go to
            while (True):
                if (self.adjacencyList[nodeIndex].addToQueue(person)): #person successfully added to queue at their next node
                    person.startWaiting()
                    break
        # self.isSimulating = False

    def run(self):
        """
        Runs the thread essentially (and calls the simulation so it runs until the thread is exited)
        """
        while not self.shouldFinish.is_set(): #so that program will end when you want it to
            self.shouldWork.wait()
            self.startSimulation()
            self.shouldWork.clear()
    
    def stop(self):
        """Ends the program"""
        for node in self.adjacencyList:
            node.stop()
        self.shouldWork.set() # just in case the thread is waiting at the time this is called
        self.shouldFinish.set()

    def __str__(self):
        return self.name


#Represents the last node in the graph. When a person reaches this node, information about their path through security
#is written to a csv file. When the last person reaches this node, the program terminates.
class EndNode(Node):
    def __init__(self, filename):
        """
        Creates a new EndNode that will write to the given file.
        :param filename: file the node will write its information to
        """
        Node.__init__(self, 0, None, None, 0, 1000, "end")
        self.count = 0
        self.numPeople = 0
        self.graph = None #will get sets from inside the Graph class
        self.filename = filename
        self.startTime = 0

    def addToQueue(self, person):
        """
        Finishes a passenger's trip through security and writes out their data to a csv file.
        :param person: person who has reached the end of security
        :return: true (person is always added to the queue because they spend no time at this node so line never grows)
        """
        import time
        global count #order in which people finish
        global scalar
        newPersonTimes = self.formatPerson(person.timesAtNodes, person.path)
        with open(self.filename, 'a') as peoplecsv:
            peoplecsv.write('{},{},{},{},'.format(count, (time.time()-self.startTime)*scalar, person.id,person.timeSpent,sep=','))
            count += 1
            for time in newPersonTimes:
                peoplecsv.write('{},'.format(time, sep=','))
            peoplecsv.write('{}\n'.format(person.precheck, sep=','))
        self.count += 1
        if(self.count == self.numPeople): #everyone has gone through security and the program should terminate
            print("done")
            self.graph.finish()
        return True

    def formatPerson(self, timeAtNodeInfo, path):
        """
        Formats the data about a passenger's path through security so it looks nice in the csv file
        :param timeAtNodeInfo: time the person spent at each node they passed through (list)
        :param path: list of each node the passenger went through
        :return: the formatted data
        """
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
        """
        Kills the thread that is this node.
        """
        self.shouldWork.set()
        self.shouldFinish.set()