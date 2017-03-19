from node import Node, EndNode
from Person import Person
import sys
import time
from collections import namedtuple
import random
import csv
import numpy as np

if len(sys.argv) < 7:
    print("usage: python3 MainSimulation.py [filename] [time_scale] [num_people] [arrival_rate_scale] [percent_precheck] [percent_zoneD]")
    sys.exit()

scalar = int(sys.argv[2]) #how much the program is sped up (eg. 100 = 100 times faster)

class Graph:
    def __init__(self,startNodes,endNode,nodeList):
        """
        Creates a new graph object with the given start nodes, end node, and node list.
        :param startNodes: start nodes (one for TSA Pre-Check and one for regular lanes)
        :param endNode: last node in the graph
        :param nodeList: list of nodes from end to start
        """
        self.startNodes = startNodes
        self.endNode = endNode
        self.nodeList = nodeList #list of nodes from end to start
        endNode.graph = self

    def addPerson(self):
        """
        Adds a person to the graph. Generates a random number between 0 and 1 and if the number is less than the input
        value of percent precheck (sys.argv[5]), adds that person to the precheck lane. Otherwise, adds that person to
        the regular lane.
        """
        p = Person()
        p.startWaiting()
        s = 0
        if random.random() < .01*float(sys.argv[5]):
            s += 1
            p.precheck = 1
        self.startNodes[s].addToQueue(p)

    def simulate(self,numPeople):
        """
        Simulates running people through the graph at intervals following a distribution found using problem data. Opens
        a csv file with the specified file name (sys.argv[1]) and writes data gathered as people travel through.
        :param numPeople: number of people to run through the graph
        """
        #open csv file and set it up with the proper headings
        global scalar #how much faster the program runs that it would in real life
        with open(sys.argv[1], 'w') as peoplecsv:
            writer = csv.writer(peoplecsv, delimiter=',')
            writer.writerow(['order finished', 'relative system time', 'person id', 'total time spent', 'initial line time',
                             'id check time', 'drop off time', 'ait time', 'pat down time', 'pick up time',
                             'bag check time', 'precheck'])
            startTime = time.time()
            self.endNode.startTime = startTime
        #start all the threads
        for node in self.nodeList:
            node.start()
        self.endNode.numPeople = numPeople
        for i in range(numPeople):
            self.addPerson()
            time.sleep(self.generateRandomSeconds()/scalar) #so the arrival of people is spaced out appropriately

    def finish(self):
        """
        Kills all the threads when people are finished going through the graph.
        """
        for startNode in self.startNodes:
            startNode.stop()
        sys.exit()

    @staticmethod
    def generateRandomSeconds():
        """
        Generates the amount of time (in seconds) between people arriving at the security checkpoint based on the data
        given in the problem statement. Can be scaled up or down using sys.argv[4].
        :return: amount of time the thread should sleep before adding another person to the queue.
        """
        r = random.random()
        scale = float(sys.argv[4])
        if r < .3913:
            return 2.5*scale
        elif r < .543:
            return 7.5*scale
        elif r < .696:
            return 12.5*scale
        elif r < .826:
            return 17.5*scale
        elif r<.891:
            return 22.5*scale
        elif r<.913:
            return 27.5*scale
        elif r<.935:
            return 32.5*scale
        elif r<.957:
            return 52.5*scale
        elif r<.978:
            return 57.5*scale
        else:
            return 77.5*scale

def getIndicesOfNum(num, twoDList):
    """
    Gets the indices (of the outer array) of num in a 2D list
    :param num: number whose indices we wish to find
    :param twoDList: the list where num's indices will be found
    :return: the indices of num in the 2D list
    """
    indices = []
    for i in range(0, len(twoDList)):
        for j in range(0, len(twoDList[i])):
            if(twoDList[i][j] == num):
                indices.append(i)
                break
    return indices

def isInt(string):
    """
    Tests if a string can be parsed into an integer or not.
    :param string: string to be tested
    :return: true if the string can be parsed as an int, false otherwise.
    """
    try:
        int(string)
        return True
    except ValueError:
        return False

SecurityLevel = namedtuple("SecurityLevel", "numElements defaultConnections allConnections zoneDConnections")

#####CREATE THE GRAPH HERE##################
def makeGraph(startLevel,idCheckLevel,dropOffLevel,aitLevel, numberOfZoneDbagCheck): # the first four must be SecurityLevel named tuples
    #################CHOICE FUNCTIONS#####################################################################
    def defaultChoiceFn(choicesList,default=0,prevPath=[]):
        """People in line always choose the node in front of them (specified as default)"""
        return default

    def strictMinimumFn(choicesList,default=0,prevPath=[]):
        """People choose the node with the shortest line no matter what"""
        if len(choicesList) <= 1:
            return 0
        if choicesList[default] == min(choicesList):
            return default
        try:
            return choicesList.index(min(choicesList))
        except ValueError:
            #print("Something is truly wrong here: the minimum element is not in the array...")
            return 0

    def pickUpNodeChoiceFn(choicesList,default=0,prevPath=[]):
        """
        People either get sent to zone D with their bags (and go to the one with the shortest line) or go to the end
        node (which means they are through security). The end node is always choice 0, the zone D bag check nodes are
        choices 1,2,...
        :param choicesList: list of node choices that passenger has
        """
        randNum = random.random()
        if(randNum<.02):  #2% of bags go to zone D
            zoneDchoicesList = choicesList[1:]
            if(len(choicesList) == 2):
                return 1
            return choicesList.index(min(zoneDchoicesList)) #return index of zoneD with fewest people waiting
        else:
            return default

    def aitChoiceFn(choicesList,default=0,prevPath=[]): #go back to the scanner you came from or go to zone D
        """
        People either get sent to zone D (patdown) with chance sys.argv[6] or they go back to the scanner that
        they came from.
        :param choicesList: list of node choices that passenger has (based on edges)
        :param prevPath: previous path the passenger took
        :return: index of the next node the passenger will go to.
        """
        randNum = random.random()
        zoneDPercent = float(sys.argv[6])
        if (randNum < zoneDPercent):
            return len(choicesList)-1 #only one possibe pat down node to go to
        else: #figure out which scanner that passenger came from and send them back to that one
            dropOffNode = prevPath[-2]
            startIndex = len(dropOffNode)-1
            for letter in range(len(dropOffNode)):
                if(isInt(dropOffNode[letter])):
                    startIndex = letter
                    break
            index = int(dropOffNode[startIndex:])
            return index

    def zoneDPatdownChoiceFn(choicesList,default=0,prevPath=[]):
        """
        Determines which scanner the passenger came from and sends them back to that same scanner to pick up their bags
        :param prevPath: previous path the passenger took (has the drop off node on it)
        :return: the index of the next node that should be chosen
        """
        dropOffNode = prevPath[-3]
        startIndex = len(dropOffNode) - 1
        for letter in range(len(dropOffNode)):
            if (isInt(dropOffNode[letter])):
                startIndex = letter
                break
        index = int(dropOffNode[startIndex:])
        return index

    def relativeMinFn(choicesList, default=0, prevPath = []): #chooses the shortest path if it is obviously shorter, otherwise chooses default path
        """
        Passenger chooses the shortest line if it is obviously shorter than the default line (less than 2/3 as long -
        this was an arbitrary choice).
        :param choicesList: list of nodes that the passenger could choose to go to
        :param default: node that the passenger will default too if no line is obviously shorter
        :return: index of the node in choicesList that the passenger has chosen
        """
        if len(choicesList) <= 1:
            return 0
        minLine = min(choicesList)
        if (choicesList[default] == minLine):
            return default
        if(minLine == 0): #if there is an empty line other than the default you will automatically go there
            return choicesList.index(minLine)
        if(choicesList[default]/minLine >= 1.5): #one line is significantly shorter than default
            return choicesList.index(minLine)
        else:
            return default

    ###############################TIME FUNCTIONS#####################################################################
    def zoneDPatdownTimeFunction(path):
        """Calculates the amount of time a passenger will spend getting patted down based on a normal distribution"""
        #return 20/scalar
        t = np.random.normal(20, 2)/scalar
        if(t<3/scalar):
            return 3/scalar
        else:
            return t

    def zoneDBagCheckTimeFunction(path): #5 minutes
        """Calculates the amount of time a passenger will spend getting their bag checked in Zone D based on a normal distribution"""
        #return 120/scalar
        t = np.random.normal(120, 60) / scalar
        if (t < 30/scalar):
            return 30/scalar
        else:
            return t

    def pickUpNodeTimeFunction(path):
        """Calculates the amount of time a passenger will spend picking up their bags based on a normal distribution"""
        if(path[0][-1] == "0"): #regular line
            #return 45/scalar
            t = np.random.normal(45, 5) / scalar
            if (t < 5/scalar):
                return 5/scalar
            else:
                return t
        else: #tsa precheck line (faster)
            #return 25/scalar
            t = np.random.normal(25, 5) / scalar
            if (t < 5/scalar):
                return 5/scalar
            else:
                return t

    def aitTimeFunction(path):
        """Calculates the amount of time a passenger will spend going through the AIT based on a normal distribution"""
        #return 15/scalar
        t = np.random.normal(15, 5.8)/scalar
        if(t<3.5/scalar):
            return 3.5/scalar
        else:
            return t

    def dropOffTimeFunction(path):
        """Calculates the amount of time a passenger will spend dropping off their baggage based on a normal distribution"""
        if(path[0][-1] == "0"): #regular line
            #return 45/scalar
            t = np.random.normal(45, 10) / scalar
            if (t < 5/scalar):
                return 5/scalar
            else:
                return t
        else: #TSA pre-check (faster)
            #return 25/scalar
            t = np.random.normal(25, 5) / scalar
            if (t < 5/scalar):
                return 5/scalar
            else:
                return t

    def idCheckTimeFunction(path):
        """Calculates the amount of time a passenger will spend getting their ID checked based on a normal distribution"""
        #return 15/scalar
        t = np.random.normal(15,3.8)/scalar
        if(t<5/scalar):
            return 5/scalar
        else:
            return t

    def startTimeFunction(path):
        """Passengers spend no time at the start node (just there to hold a line)"""
        return 0

    # endNode = EndNode()
    # pickUpNode = Node(2, defaultChoiceFn, [endNode], 100, "pickUp")
    # aitNode = Node(1.3, defaultChoiceFn, [pickUpNode], 100, "ait")
    # dropOffNode = Node(2, defaultChoiceFn, [aitNode], 100, "dropOff")
    # idCheckNode = Node(1.3, defaultChoiceFn, [dropOffNode], 100, "idCheck")
    # startNode = Node(0, defaultChoiceFn, [idCheckNode], 100, "start")
    # nodeList = [endNode, pickUpNode, aitNode, dropOffNode, idCheckNode, startNode]

    global scalar

    endNode = EndNode(sys.argv[1]) #create a new EndNode with the input file name

    #Create the graph via lists of nodes
    zoneDBagCheckNodeList = []
    for i in range(numberOfZoneDbagCheck):
        zoneDBagCheckNodeList.append(Node(zoneDBagCheckTimeFunction, defaultChoiceFn, [endNode], 0, 100, "zoneDbagcheck" + str(i))) #10 people can be in zone D

    pickUpNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = [endNode]
        for j in dropOffLevel.zoneDConnections[i]:
            adjacencyList.append(zoneDBagCheckNodeList[j])
        pickUpNodeList.append(Node(pickUpNodeTimeFunction, pickUpNodeChoiceFn, adjacencyList, 0, 15, "pickUp" + str(i)))

    zoneDPatdownNodeList = []
    for i in range(aitLevel.numElements): #one patdown area for each AIT
        adjacencyList = []
        for j in range(dropOffLevel.numElements): #can't really go to all drop offs but need a list of all of them so the index specified by person.path in choice function matches
            adjacencyList.append(pickUpNodeList[j])
        try:
            defaultIndex = dropOffLevel.defaultConnections.index(i)
        except ValueError:
            defaultIndex = 0
        zoneDPatdownNodeList.append(Node(zoneDPatdownTimeFunction, zoneDPatdownChoiceFn, adjacencyList, defaultIndex, 2, "zoneDpatdown" + str(i)))

    aitNodeList = []
    for i in range(aitLevel.numElements):
        adjacencyList = []
        #for j in getIndicesOfNum(i, dropOffLevel.allConnections):
        for j in range(dropOffLevel.numElements): #can't really go to all drop offs but need a list of all of them so the index specified by person.path matches
            adjacencyList.append(pickUpNodeList[j])
        adjacencyList.append(zoneDPatdownNodeList[i])
        try:
            defaultIndex = dropOffLevel.defaultConnections.index(i)
        except ValueError:
            defaultIndex = 0 # the function must take care of it anyway
        aitNodeList.append(Node(aitTimeFunction, aitChoiceFn, adjacencyList, defaultIndex,  3, "ait" + str(i)))
    
    dropOffNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = []
        for ait in dropOffLevel.allConnections[i]:
            adjacencyList.append(aitNodeList[ait])
        dropOffNodeList.append(Node(dropOffTimeFunction, relativeMinFn, adjacencyList, dropOffLevel.defaultConnections[i], 10, "dropOff" + str(i)))
    
    idCheckNodeList = []
    for i in range(idCheckLevel.numElements):
        adjacencyList = []
        for dropOff in idCheckLevel.allConnections[i]:
            adjacencyList.append(dropOffNodeList[dropOff])
        idCheckNodeList.append(Node(idCheckTimeFunction, relativeMinFn, adjacencyList, idCheckLevel.defaultConnections[i], 1, "idCheck" + str(i)))
    
    startNodeList = []
    for i in range(startLevel.numElements):
        adjacencyList = []
        for idCheck in startLevel.allConnections[i]:
            adjacencyList.append(idCheckNodeList[idCheck])
        startNodeList.append(Node(startTimeFunction, strictMinimumFn, adjacencyList, startLevel.defaultConnections[i], 10000, "start" + str(i)))
  #  startNode = Node(0, defaultChoiceFn, idCheckNodeList, 0, 100, "start")
    


    nodeList = [endNode]
    nodeList = nodeList + zoneDBagCheckNodeList + pickUpNodeList + zoneDPatdownNodeList + aitNodeList + dropOffNodeList + idCheckNodeList
    nodeList.extend(startNodeList)

    g = Graph(startNodeList, endNode, nodeList)
    g.simulate(int(sys.argv[3]))

    # p = Person()
    # p.startWaiting()
    # startNode.addToQueue(p)

def defaultFourLanes():
    """
    Creates the inputs to make a graph with 1 Pre-Check lane and 3 regular lanes
    :return: the input to makeGraph()
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1],[2]],None)
    idCheckLevel = SecurityLevel(3,[1,1,0],[[0,1,2],[0,1,2],[3]],None)
    dropOffTuple = SecurityLevel(4,[0,1,0,0],[[0,1],[0,1],[2],[3]],[[0],[0],[1],[1]])
    aitTuple = SecurityLevel(4,None,None,None)
    numBagChecks = 2
    return (startLevel,idCheckLevel,dropOffTuple,aitTuple,numBagChecks)

def threePreCheckFourLanes():
    """
    Creates the inputs to make a graph with 3 pre-check lanes and 1 regular lane
    :return: the input to makeGraph()
    """
    startLevel = SecurityLevel(2,[0,0],[[0],[1,2]],None)
    idCheckLevel = SecurityLevel(3,[0,1,1],[[0],[1,2,3],[1,2,3]],None)
    dropOffLevel = SecurityLevel(4,[0,0,0,1],[[0],[1],[2,3],[2,3]],[[0],[0],[1],[1]])
    aitLevel = SecurityLevel(4,None,None,None)
    numBagChecks = 2
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def twoPreCheckFourLanes():
    """
    Creates the inputs to make a graph with 2 pre-check lanes and 2 regular lanes
    :return: the input to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1],[2]],None)
    idCheckLevel = SecurityLevel(3,[0,1,0],[[0,1],[0,1],[2,3]],None)
    dropOffLevel = SecurityLevel(4,[0,1,0,1],[[0,1],[0,1],[2,3],[2,3]],[[0],[0],[1],[1]])
    aitLevel = SecurityLevel(4,None,None,None)
    numBagChecks = 2
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def onePreCheckFiveLanesThreeID():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, and 3 ID check points
    :return: the input to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2],[3]],None)
    idCheckLevel = SecurityLevel(4,[1,2,2,0],[[0,1,2,3],[0,1,2,3],[0,1,2,3],[4]],None)
    dropOffLevel = SecurityLevel(5,[0,1,0,1,0],[[0,1],[0,1],[2,3],[2,3],[4]],[[0],[0],[1],[1],[2]])
    aitLevel = SecurityLevel(5,None,None,None)
    numBagChecks = 3
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def onePreCheckFiveManyPossibilities():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, and maximum versatility of movement
    :return: the input to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2,3],[4]],None)
    idCheckLevel = SecurityLevel(5,[0,1,2,3,0],[[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3],[4]],None)
    dropOffLevel = SecurityLevel(5,[0,1,0,1,0],[[0,1],[0,1],[2,3],[2,3],[4]],[[0],[0],[1],[1],[2]])
    aitLevel = SecurityLevel(5,None,None,None)
    numBagChecks = 3
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def onePreCheckFiveLinesTwoHalves():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, and no movement between each pair of regular lanes
    :return: the input to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2,3],[4]],None)
    idCheckLevel = SecurityLevel(5,[0,1,0,1,0],[[0,1],[0,1],[2,3],[2,3],[4]],None)
    dropOffLevel = SecurityLevel(5,[0,1,0,1,0],[[0,1],[0,1],[2,3],[2,3],[4]],[[0],[0],[1],[1],[2]])
    aitLevel = SecurityLevel(5,None,None,None)
    numBagChecks = 3
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def onePreCheckFiveLinesSeparated():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, and no movement between any lanes
    :return: the inputs to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2,3],[4]],None)
    idCheckLevel = SecurityLevel(5,[0,0,0,0,0],[[0],[1],[2],[3],[4]],None)
    dropOffLevel = SecurityLevel(5,[0,0,0,0,0],[[0],[1],[2],[3],[4]],[[0],[0],[1],[1],[2]])
    aitLevel = SecurityLevel(5,None,None,None)
    numBagChecks = 3
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def onePreCheckFiveIDThreeAIT():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, and 4 AITs
    :return: the inputs to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2,3],[4]],None)
    idCheckLevel = SecurityLevel(5,[0,0,1,1,0],[[0,1],[0,1],[0,1],[0,1],[2]],None)
    dropOffLevel = SecurityLevel(3,[1,0,0],[[0,1],[1,2],[3]],[[0],[0],[1]])
    aitLevel = SecurityLevel(4,None,None,None)
    numBagChecks = 2
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)


def onePreCheckFiveKGraph():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, 5 ID checks, 5 scanners, and 3 AITs
    :return: the inputs to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2,3],[4]],None)
    idCheckLevel = SecurityLevel(5,[0,1,2,3,0],[[0,1,2,3],[0,1,2,3],[0,1,2,3],[0,1,2,3],[4]],None)
    dropOffLevel = SecurityLevel(5,[0,0,0,0,0],[[0],[0],[1],[1],[2]],[[0],[0],[1],[1],[2]])
    aitLevel = SecurityLevel(3,None,None,None)
    numBagChecks = 3
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)

def onePreCheckFourIDThreeScanFourAIT():
    """
    Creates the inputs to make a graph with 1 pre-check lane, 4 regular lanes, 5 ID checks, 4 scanners, and 5 AITs
    :return: the inputs to makeGraph
    """
    startLevel = SecurityLevel(2,[1,0],[[0,1,2,3],[4]],None)
    idCheckLevel = SecurityLevel(5,[0,1,1,2,0],[[0,1,2],[0,1,2],[0,1,2],[0,1,2],[3]],None)
    dropOffLevel = SecurityLevel(4,[1,1,0,0],[[0,1],[1,2],[2,3],[4]],[[0],[0],[1],[1]])
    aitLevel = SecurityLevel(5,None,None,None)
    numBagChecks = 2
    return (startLevel,idCheckLevel,dropOffLevel,aitLevel,numBagChecks)


random.seed()


#be careful, the second argument is indexes of the elements of the third argument 
startLevel = SecurityLevel(2,[1,0],[[0,1], [2]], None)
idCheckTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]], None)
dropOffTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]], [[0], [0], [1]]) #last argument is the zone D bag checks that the given scanner feeds in to (should have the
                                                                                    #same number of sublists as there are scanners)
aitTuple = SecurityLevel(3,None,None, None)
args = defaultFourLanes()
makeGraph(*args)
#makeGraph(startLevel,idCheckTuple,dropOffTuple,aitTuple, 2)
#makeGraph(2,3,3, #numIDCheckNodes, numScanners, numAITS
#          [[0,1], [1,2]], #idCheckToDropOff
#          [[0,1], [0,1,2], [2]]) #dropOffForAITS



