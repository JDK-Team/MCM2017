from node import Node, EndNode
from Person import Person
import sys
import time
from collections import namedtuple
import random
scalar = 100

class Graph:
    
    def __init__(self,startNodes,endNode,nodeList):
        self.startNodes = startNodes
        self.endNode = endNode
        self.nodeList = nodeList #list of nodes from end to start
        endNode.graph = self

    def addPerson(self):
        p = Person()
        p.startWaiting()
        s = 0
        if random.random() < 0.45:
            s += 1
        self.startNodes[s].addToQueue(p)

    def simulate(self,numPeople):
        global scalar
        #start all the threads
        for node in self.nodeList:
            print(node, "adjacency list: ", node.adjacencyList)
            node.start()
        self.endNode.numPeople = numPeople
        for i in range(numPeople):
            self.addPerson()
            time.sleep(self.generateRandomSeconds()/scalar)

    def finish(self):
        for startNode in self.startNodes:
            startNode.stop()
        sys.exit()

    @staticmethod
    def generateRandomSeconds():
        r = random.random()
        if r < .3913:
            return 1
        elif r < .543:
            return 5
        elif r < .696:
            return 10
        elif r < .826:
            return 15
        else:
            return 20

def getIndicesOfNum(num, twoDList):
    indices = []
    for i in range(0, len(twoDList)):
        for j in range(0, len(twoDList[i])):
            if(twoDList[i][j] == num):
                indices.append(i)
                break
    return indices

def isInt(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

SecurityLevel = namedtuple("SecurityLevel", "numElements defaultConnections allConnections zoneDConnections")

#def makeGraph(numIDcheckNodes, numScanners, numAITS, idCheckToDropoff, dropOffForAITS): #dropOffForAITS is a 2-d list of length numScanners that says which AIT(s) the scanner goes to (0 goes to 0 (or more) always)
def makeGraph(startLevel,idCheckLevel,dropOffLevel,aitLevel, numberOfZoneDbagCheck): # the first four must be SecurityLevel named tuples
    #################CHOICE FUNCTIONS#####################################################################
    def defaultChoiceFn(choicesList,default=0,prevPath=[]):
        return default
    def strictMinimumFn(choicesList,default=0,prevPath=[]):
        #print("MINFUNC: ",choicesList,default)
        if len(choicesList) <= 1:
            return 0
        if choicesList[default] == min(choicesList):
            return default
        try:
            return choicesList.index(min(choicesList))
        except ValueError:
            print("Something is truly wrong here: the minimum element is not in the array...")
            return 0
    def pickUpNodeChoiceFn(choicesList,default=0,prevPath=[]): #end node is always choice 0, zone D bag check nodes are indices 1,2,...
        randNum = random.random()
        if(randNum<.01): #1% of people go to zone D and 1% of bags go to zone D
            zoneDchoicesList = choicesList[1:]
            if(len(choicesList) == 2):
                return 1
            return choicesList.index(min(zoneDchoicesList)) #return index of zoneD with fewest people waiting
        else:
            return default
    def aitChoiceFn(choicesList,default=0,prevPath=[]): #go back to the scanner you came from or go to zone D
        randNum = random.random()
        if (randNum < .01):  # 1% of people go to zone D and 1% of bags go to zone D
            zoneDchoices = choicesList[1:]
            if (len(choicesList) == 2):
                return 1
            return choicesList.index(min(zoneDchoices))  # return index of zoneD with fewest people waiting
        else:
            dropOffNode = prevPath[-2]
            startIndex = len(dropOffNode)-1
            for letter in range(len(dropOffNode)):
                if(isInt(dropOffNode[letter])):
                    startIndex = letter
                    break
            index = int(dropOffNode[startIndex:])
            return index
    def zoneDPatdownChoiceFn(choicesList,default=0,prevPath=[]):
        dropOffNode = prevPath[-3]
        startIndex = len(dropOffNode) - 1
        for letter in range(len(dropOffNode)):
            if (isInt(dropOffNode[letter])):
                startIndex = letter
                break
        index = int(dropOffNode[startIndex:])
        return index


    ###############################TIME FUNCTIONS#####################################################################
    def zoneDPatdownTimeFunction(path):
        return 20/scalar
    def zoneDBagCheckTimeFunction(path):
        return 300/scalar
    def pickUpNodeTimeFunction(path):
        if(path[0][-1] == "0"): #regular line
            return 8.5/scalar
        else: #tsa precheck line
            return 5/scalar
    def aitTimeFunction(path):
        return 11.5/scalar
    def dropOffTimeFunction(path):
        if(path[0][-1] == "0"): #regular line
            return 8.5/scalar
        else:
            return 5/scalar
    def idCheckTimeFunction(path):
        return 11.5/scalar
    def startTimeFunction(path):
        return 0

    # endNode = EndNode()
    # pickUpNode = Node(2, defaultChoiceFn, [endNode], 100, "pickUp")
    # aitNode = Node(1.3, defaultChoiceFn, [pickUpNode], 100, "ait")
    # dropOffNode = Node(2, defaultChoiceFn, [aitNode], 100, "dropOff")
    # idCheckNode = Node(1.3, defaultChoiceFn, [dropOffNode], 100, "idCheck")
    # startNode = Node(0, defaultChoiceFn, [idCheckNode], 100, "start")
    # nodeList = [endNode, pickUpNode, aitNode, dropOffNode, idCheckNode, startNode]

    global scalar

    endNode = EndNode()

    zoneDBagCheckNodeList = []
    for i in range(numberOfZoneDbagCheck):
        zoneDBagCheckNodeList.append(Node(zoneDBagCheckTimeFunction, defaultChoiceFn, [endNode], 0, 10, "zoneDbagcheck" + str(i))) #10 people can be in zone D

    pickUpNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = [endNode]
        for j in dropOffLevel.zoneDConnections[i]:
            adjacencyList.append(zoneDBagCheckNodeList[j])
        pickUpNodeList.append(Node(pickUpNodeTimeFunction, pickUpNodeChoiceFn, adjacencyList, 0, 100, "pickUp" + str(i)))

    zoneDPatdownNodeList = []
    for i in range(aitLevel.numElements): #one patdown area for each AIT
        adjacencyList = []
        for j in range(dropOffLevel.numElements): #can't really go to all drop offs but need a list of all of them so the index specified by person.path in choice function matches
            adjacencyList.append(pickUpNodeList[j])
        try:
            defaultIndex = dropOffLevel.defaultConnections.index(i)
        except ValueError:
            defaultIndex = 0
        zoneDPatdownNodeList.append(Node(zoneDPatdownTimeFunction, zoneDPatdownChoiceFn, adjacencyList, defaultIndex, 5, "zoneDpatdown" + str(i)))

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
        aitNodeList.append(Node(aitTimeFunction, aitChoiceFn, adjacencyList, defaultIndex,  100, "ait" + str(i)))
    
    dropOffNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = []
        for ait in dropOffLevel.allConnections[i]:
            adjacencyList.append(aitNodeList[ait])
        dropOffNodeList.append(Node(dropOffTimeFunction, defaultChoiceFn, adjacencyList, dropOffLevel.defaultConnections[i], 20, "dropOff" + str(i)))
    
    idCheckNodeList = []
    for i in range(idCheckLevel.numElements):
        adjacencyList = []
        for dropOff in idCheckLevel.allConnections[i]:
            adjacencyList.append(dropOffNodeList[dropOff])
        idCheckNodeList.append(Node(idCheckTimeFunction, defaultChoiceFn, adjacencyList, idCheckLevel.defaultConnections[i], 1, "idCheck" + str(i)))
    
    startNodeList = []
    for i in range(startLevel.numElements):
        adjacencyList = []
        for idCheck in startLevel.allConnections[i]:
            adjacencyList.append(idCheckNodeList[idCheck])
        startNodeList.append(Node(startTimeFunction, strictMinimumFn, adjacencyList, startLevel.defaultConnections[i], 100, "start" + str(i)))
  #  startNode = Node(0, defaultChoiceFn, idCheckNodeList, 0, 100, "start")
    


    nodeList = [endNode]
    nodeList = nodeList + zoneDBagCheckNodeList + pickUpNodeList + zoneDPatdownNodeList + aitNodeList + dropOffNodeList + idCheckNodeList
    nodeList.extend(startNodeList)
    # for node in nodeList:
    #     node.start()

    g = Graph(startNodeList, endNode, nodeList)
    g.simulate(100)

    # p = Person()
    # p.startWaiting()
    # startNode.addToQueue(p)

random.seed(a=1)

#be careful, the second argument is indexes of the elements of the third argument 
startLevel = SecurityLevel(2,[1,0],[[0,1], [2]], None)
idCheckTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]], None)
dropOffTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]], [[0], [0], [1]]) #last argument is the zone D bag checks that the given scanner feeds in to (should have the
                                                                                    #same number of sublists as there are scanners)
aitTuple = SecurityLevel(3,None,None, [[0],[0],[1]])

makeGraph(startLevel,idCheckTuple,dropOffTuple,aitTuple, 2)
#makeGraph(2,3,3, #numIDCheckNodes, numScanners, numAITS
#          [[0,1], [1,2]], #idCheckToDropOff
#          [[0,1], [0,1,2], [2]]) #dropOffForAITS



